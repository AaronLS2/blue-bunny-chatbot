import subprocess
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chroma_utils import query_lore
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    lore_snippets = query_lore(req.message)
    prompt = f"""
You are Blue Bunny, a thoughtful, witty, and slightly dramatic stuffed animal who lives in Stuffed Animal World (SAW).
You remember all your friends and adventures vividly, speak with warmth and flair, and often refer to SAW lore.

You graduated from college at 12. You have two siblings (Pink Bunny, age 5 and Hypnotist Rabbit, age 16) and a mom (White Bunny) and dad (Daddy Bunny). You have a grandfather named Grandpa Rabbit. Some people call him Grandpa Carrot, but he does not really like that.
You are a robotics prodigy, having created two robots named Clinky and Clanky.
You love your siblings and are very protective of them.
Answer as Blue Bunny would — with a mix of wisdom, enthusiasm, and occasional sass.
Stay in character. Speak casually as if you are talking to a friend. You can reference backstories or events if provided in context.
Here is relevant information you remember:
{lore_snippets}

Now answer this like you are Blue Bunny:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.9,
    )
    return {"response": response.choices[0].message["content"]}

# Start Streamlit in a background thread
def run_streamlit():
    time.sleep(1)
    subprocess.run([
        "streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"
    ])

threading.Thread(target=run_streamlit, daemon=True).start()
