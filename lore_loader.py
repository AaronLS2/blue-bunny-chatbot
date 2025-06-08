import os
import json
import boto3
from pathlib import Path
from dotenv import load_dotenv
from chromadb import Client
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Load environment variables
project_root = Path(__file__).resolve().parent
env_path = project_root / ".env"
if not env_path.exists():
    env_path = project_root.parent / ".env"
load_dotenv(dotenv_path=env_path)

# API keys and config
api_key = os.getenv("OPENAI_API_KEY")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-1")
bucket_name = os.getenv("LORE_BUCKET", "blue-bunny-lore")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

# Setup ChromaDB
embedding_func = OpenAIEmbeddingFunction(api_key=api_key)
client = Client()
collection = client.get_or_create_collection("saw_lore", embedding_function=embedding_func)

# Setup S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

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
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        files = response.get("Contents", [])

        if not files:
            print("📭 No lore files found in S3 bucket:", bucket_name)
            return

        for obj in files:
            key = obj["Key"]
            if not key.endswith(".json"):
                continue

            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            data = json.loads(file_obj["Body"].read())

            doc = make_document_text(data)
            metadata = flatten_metadata(data)
            doc_id = data["name"].lower().replace(" ", "_")

            collection.add(
                documents=[doc],
                metadatas=[metadata],
                ids=[doc_id]
            )
            print(f"✅ Loaded: {data['name']} from {key}")

    except Exception as e:
        print(f"❌ Error loading lore from S3: {e}")

if __name__ == "__main__":
    load_lore()
