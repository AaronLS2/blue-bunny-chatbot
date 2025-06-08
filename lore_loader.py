import os
import json
from pathlib import Path
from dotenv import load_dotenv
from chromadb import Client
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Load environment variables from .env
project_root = Path(__file__).resolve().parent
env_path = project_root / ".env"
if not env_path.exists():
    env_path = project_root.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Check for API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

# Set up ChromaDB with OpenAI embeddings
embedding_func = OpenAIEmbeddingFunction(api_key=api_key)
client = Client()
collection = client.get_or_create_collection("saw_lore", embedding_function=embedding_func)

# Path to lore directory
LORE_DIR = Path(__file__).resolve().parent.parent / "frontend" / "lore"
print(f"🔍 Resolved lore path: {LORE_DIR}")

def make_document_text(data):
    return f"""{data['name']} is a {data['species']} who lives in {data['location']}.
Their personality is: {data['personality']}.
Abilities: {', '.join(data.get('abilities', []))}
Friends: {', '.join(data.get('friends', []))}
Family: {', '.join(data.get('family', []))}
Backstory: {data['backstory']}
Tags: {', '.join(data.get('tags', []))}
"""

def flatten_metadata(data):
    return {
        "name": data.get("name", ""),
        "species": data.get("species", ""),
        "location": data.get("location", ""),
        "personality": data.get("personality", ""),
        "backstory": data.get("backstory", ""),
        "abilities": ", ".join(data.get("abilities", [])),
        "friends": ", ".join(data.get("friends", [])),
        "family": ", ".join(data.get("family", [])),
        "tags": ", ".join(data.get("tags", []))
    }

def load_lore():
    if not LORE_DIR.exists():
        print("🚫 Lore folder not found:", LORE_DIR)
        return

    files = list(LORE_DIR.glob("*.json"))
    if not files:
        print("📭 No lore files found in", LORE_DIR)
        return

    for path in files:
        try:
            with open(path, "r") as f:
                data = json.load(f)
                doc = make_document_text(data)
                metadata = flatten_metadata(data)
                doc_id = data["name"].lower().replace(" ", "_")

                collection.add(
                    documents=[doc],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                print(f"✅ Loaded: {data['name']}")
        except Exception as e:
            print(f"❌ Failed to load {path.name}: {e}")

if __name__ == "__main__":
    load_lore()
