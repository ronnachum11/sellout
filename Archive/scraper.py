import sys
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import torch
from transformers import GPT2Tokenizer, GPT2Model
from urllib.parse import urljoin, urlparse
import pinecone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import deque
import json

# Initialize tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2Model.from_pretrained('gpt2')

def create_pinecone_index(api_key, environment, index_name):
    pinecone.init(api_key=api_key, environment=environment)
    # pinecone.create_index(index_name, dimension=768, metric="cosine")
    index = pinecone.Index(index_name=index_name)
    return index

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def extract_text(soup):
    if soup.find(id="main-content"):
        main_content = soup.find(id="main-content")
    elif soup.find(id="main"):
        main_content = soup.find(id="main")
    else:
        soup_texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, soup_texts)
        return ' '.join(t.strip() for t in visible_texts)

    return ' '.join(t.strip() for t in main_content.findAll(text=True))

def is_similar_text(new_text, texts, vectorizer):
    if not texts:
        return False
    
    tfidf_matrix = vectorizer.fit_transform(texts + [new_text])
    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
    
    return any(similarity > 0.9 for similarity in similarities[0])

def generate_embedding(text):
    inputs = tokenizer.encode_plus(text, return_tensors='pt', truncation=True, max_length=1024)
    
    with torch.no_grad():
        outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()[0]  # Average pooling

def scrape(url, visited, vectorizer, pinecone_index, limit=20):
    if url in visited or limit <= 0:
        return limit

    visited.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("An error occurred:", err)
        return limit

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')

    for paragraph in paragraphs:
        text = paragraph.get_text(strip=True)

        if not text or is_similar_text(text, texts, vectorizer):
            continue

        texts.append(text)
        print(f"Scraped: {url}")

        embedding = generate_embedding(text)
        key = f"{url}#{texts.index(text)}"
        pinecone_index.upsert(items={key: embedding})

        limit -= 1

    for link in soup.find_all('a', href=True):
        sub_url = urljoin(url, link['href'])

        if urlparse(sub_url).netloc == urlparse(url).netloc:
            limit = scrape(sub_url, visited, texts, vectorizer, pinecone_index, limit)

    return limit

def bfs_scrape(start_url, visited, page_texts, paragraph_texts, vectorizer, pinecone_index, limit=100000):
    queue = deque([start_url])
    vectors = []
    scraped_pages = 0
    text_dict = {}
    iteration = 0  # Add an iteration counter

    while queue and scraped_pages < limit:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("An error occurred:", err)
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = extract_text(soup)

        if is_similar_text(page_text, page_texts, vectorizer):
            print(f"Skipped: {url}")
            continue

        print(f"Scraped: {url}")
        page_texts.append(page_text)

        paragraphs = soup.find_all('p')

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)

            if not text or is_similar_text(text, paragraph_texts, vectorizer):
                continue

            paragraph_texts.append(text)

            embedding = generate_embedding(text)
            key = f"{url}#{paragraph_texts.index(text)}"

            vectors.append({'id': key, 'values': embedding.tolist()})
            text_dict[key] = text

            if len(vectors) % 100 == 0:
                pinecone_index.upsert(vectors=vectors)
                vectors = []
                iteration += 1

                if iteration % 5 == 0:
                    # Dump the text data into a JSON file every 10 iterations
                    with open('text_data.json', 'w') as f:
                        json.dump(text_dict, f)

        scraped_pages += 1

        for link in soup.find_all('a', href=True):
            sub_url = urljoin(url, link['href'])

            if urlparse(sub_url).netloc == urlparse(url).netloc and sub_url not in visited:
                queue.append(sub_url)

    # Upsert any remaining vectors
    if vectors:
        pinecone_index.upsert(vectors=vectors)

        # Dump the remaining text data into a JSON file
        with open('text_data.json', 'w') as f:
            json.dump(text_dict, f)

    return text_dict

def main(url):
    name = urlparse(url).netloc.split('www.')[-1].split('.')[0]
    print("PARSING", name, "FROM", url)

    pinecone_index = create_pinecone_index(
        api_key="e6127714-d24a-46bd-8d2e-18378c10855e",
        environment="us-west1-gcp-free",
        index_name=f"{name}-embeddings"
    )
    
    visited = set()
    page_texts = []
    paragraph_texts = []
    vectorizer = TfidfVectorizer()

    text_dict = bfs_scrape(url, visited, page_texts, paragraph_texts, vectorizer, pinecone_index)

    with open('text_data.json', 'w') as f:
        json.dump(text_dict, f)

if __name__ == "__main__":
    url = sys.argv[1]
    main(url)
