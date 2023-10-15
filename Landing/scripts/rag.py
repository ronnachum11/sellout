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
