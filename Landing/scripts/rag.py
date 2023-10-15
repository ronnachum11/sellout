from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.memory import ChatMessageHistory
from uuid import uuid4
import time

from langchain.tools import BaseTool, Tool
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import superpowered
import os
from pydantic.dataclasses import dataclass
import time


OPENAI_API_KEY= "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"

import superpowered

# import requests
# from bs4 import BeautifulSoup
# from tqdm import tqdm
# import json

# def getdata(url):
#     r = requests.get(url)
#     return r.text

# def get_links(website_link):
#     dict_href_links = {}

#     html_data = getdata(website_link)
#     soup = BeautifulSoup(html_data, "html.parser")
#     list_links = []
#     for link in soup.find_all("a", href=True):

#         # Append to list if new link contains original link
#         if str(link["href"]).startswith((str(website_link))):
#             list_links.append(link["href"])

#         # Include all href that do not start with website link but with "/"
#         if str(link["href"]).startswith("/"):
#             if link["href"] not in dict_href_links:
#                 # print(link["href"])
#                 dict_href_links[link["href"]] = None
#                 link_with_www = website_link + link["href"][1:]
#                 # print("adjusted link =", link_with_www)
#                 list_links.append(link_with_www)

#     # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
#     dict_links = dict.fromkeys(list_links, "Not-checked")
#     return dict_links

# def get_subpage_links(l):
#     for link in l:
#         # If not crawled through this page start crawling and get links
#         if l[link] == "Not-checked":
#             dict_links_subpages = get_links(link)
#             # Change the dictionary value of the link to "Checked"
#             l[link] = "Checked"
#         else:
#             # Create an empty dictionary in case every link is checked
#             dict_links_subpages = {}
#         # Add new dictionary to old dictionary
#         l = {**dict_links_subpages, **l}
#     return l


# def get_all_urls(website):
#   if not website.endswith("/"):
#     website += "/"
#   # create dictionary of website
#   dict_links = {website:"Not-checked"}

#   counter, counter2 = None, 0
#   while counter != 0:
#       counter2 += 1
#       dict_links2 = get_subpage_links(dict_links)
#       # Count number of non-values and set counter to 0 if there are no values within the dictionary equal to the string "Not-checked"
#       # https://stackoverflow.com/questions/48371856/count-the-number-of-occurrences-of-a-certain-value-in-a-dictionary-in-python
#       counter = sum(value == "Not-checked" for value in dict_links2.values())
#       # Print some statements
#       # print("")
#       # print("THIS IS LOOP ITERATION NUMBER", counter2)
#       # print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
#       # print("NUMBER OF 'Not-checked' LINKS = ", counter)
#       # print("")
#       dict_links = dict_links2
#       # Save list in json file
#       a_file = open("data.json", "w")
#       json.dump(dict_links, a_file)
#       a_file.close()
#   return dict_links

# def get_urls(url):
#     ret = get_all_urls(url)
#     ret2 = []
#     for key in ret:
#         if not (key in url or "product" in key):
#             ret2.append(key)
#     return ret2
    

def set_up_kb(title, description, urls):
    # urls = get_urls(url)
    # Create a Superpowered knowledge base
    kb = superpowered.create_knowledge_base(
        title=title,
        description=description
    )

    # Get the id of the knowledge base we want to upload the file to
    kb_id = kb["id"]

    # Add a document to your knowledge base
    for url in urls:
        superpowered.create_document_via_url(
            knowledge_base_id=kb_id,
            url=url,
            description=description
        )

    # Print all docs in kb
    # docs = superpowered.get_documents(kb_id)
    while True:
        time.sleep(5)
        docs = superpowered.list_documents(knowledge_base_id=kb_id, vectorization_status='COMPLETE')
        print(docs)
        if len(docs) == len(urls):
            break
        print(f"Waiting for {len(urls) - len(docs)} docs to vectorize...")

    print(f"\n\nKB_ID:{kb_id}\n\n")
    return kb_id

def create_query_tool(name: str, description: str, kb_id: str):
    def run(query: str) -> str:
        results = superpowered.query_knowledge_bases(
            knowledge_base_ids=[kb_id],
            query=query,
            summarize_results=True
        )
        return results["summary"]

    return Tool.from_function(
        func=run,
        name=name,
        description=description
    )

def get_tool(title, description, url_list):
    kb_id = set_up_kb(title, description, url_list) 
    return create_query_tool(title, description, kb_id)