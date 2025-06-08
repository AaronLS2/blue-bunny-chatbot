# backend/chroma_utils.py

import os
from dotenv import load_dotenv
from chromadb import Client
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from pathlib import Path

# Explicitly load .env from the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Delay Chroma setup until it's needed
_chroma_client = None
_collection = None

def get_collection():
    global _chroma_client, _collection
    print("✅ API key loaded:", os.getenv("OPENAI_API_KEY"))

    if _collection is None:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

        embedding_func = OpenAIEmbeddingFunction(api_key=openai_key)
        _chroma_client = Client()
        _collection = _chroma_client.get_or_create_collection(
            "saw_lore", embedding_function=embedding_func
        )

    return _collection

def query_lore(query, k=5):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]
