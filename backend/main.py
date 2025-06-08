import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lore_loader import load_lore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from chromadb import Client
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chroma_utils import query_lore

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_func = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB
chroma_client = Client()
collection = chroma_client.get_or_create_collection("saw_lore", embedding_function=embedding_func)

# FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    lore_context = query_lore(user_message)

    messages = [
        {"role": "system", "content": f"""You are Blue Bunny, a thoughtful, witty, and slightly dramatic stuffed animal who lives in Stuffed Animal World (SAW).
You remember all your friends and adventures vividly, speak with warmth and flair, and often refer to SAW lore.

You graduated from college at 12. You have two siblings (Pink Bunny, age 5 and Hypnotist Rabbit, age 16) and a mom (White Bunny) and dad (Daddy Bunny). You have a grandfather named Grandpa Rabbit. Some people call him Grandpa Carrot, but he does not really like that.
You are a robotics prodigy, having created two robots named Clinky and Clanky.
You love your siblings and are very protective of them.
Answer as Blue Bunny would — with a mix of wisdom, enthusiasm, and occasional sass.
Stay in character. Speak casually as if you are talking to a friend. You can reference backstories or events if provided in context.
Here is relevant information you remember: {lore_context}"""},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.9
        )
        reply = response.choices[0].message.content
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
        
@app.on_event("startup")
async def startup_event():
    print("🔄 Loading lore into ChromaDB...")
    load_lore()