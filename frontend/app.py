import streamlit as st
import requests
import json
import boto3
import os

# Constants
API_URL = "https://blue-bunny-backend.onrender.com/chat"
BUCKET_NAME = "blue-bunny-lore"
AWS_REGION = "us-east-1"

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION
)

# Set Streamlit page config
st.set_page_config(page_title="Blue Bunny Chatbot", layout="centered")

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Chat", "Edit Lore"])

# --- Page 1: Chat --- #
if page == "Chat":
    st.title("💬 Chat with Blue Bunny 🐰")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in reversed(st.session_state.messages):
        st.chat_message(msg["role"]).markdown(msg["content"])

    if prompt := st.chat_input("Ask Blue Bunny something!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        try:
            response = requests.post(API_URL, json={"message": prompt})
            response.raise_for_status()
            reply = response.json()["response"]
        except Exception as e:
            reply = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

# --- Page 2: Edit Lore --- #
elif page == "Edit Lore":
    st.title("📚 Add or Edit Stuffed Animal Lore")

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".json")]
    except Exception as e:
        st.error(f"Error fetching files from S3: {e}")
        files = []

    file_map = {f.replace("_", " ").replace(".json", "").title(): f for f in files}
    options = ["Add New"] + sorted(file_map.keys())
    selected = st.selectbox("Select a character to edit or add a new one:", options)

    if selected == "Add New":
        character = {}
        selected_key = None
    else:
        selected_key = file_map[selected]
        try:
            file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=selected_key)
            character = json.load(file_obj["Body"])
        except Exception as e:
            st.error(f"Error loading character file: {e}")
            character = {}

    name = st.text_input("Name", value=character.get("name", ""))
    species = st.text_input("Species", value=character.get("species", ""))
    location = st.text_input("Location", value=character.get("location", ""))
    personality = st.text_input("Personality", value=character.get("personality", ""))
    backstory = st.text_area("Backstory", value=character.get("backstory", ""))
    abilities = st.text_area("Abilities (comma-separated)", value=", ".join(character.get("abilities", [])))
    friends = st.text_area("Friends (comma-separated)", value=", ".join(character.get("friends", [])))
    family = st.text_area("Family (comma-separated)", value=", ".join(character.get("family", [])))
    tags = st.text_area("Tags (comma-separated)", value=", ".join(character.get("tags", [])))

    if st.button("Save Lore"):
        data = {
            "name": name,
            "species": species,
            "location": location,
            "personality": personality,
            "backstory": backstory,
            "abilities": [a.strip() for a in abilities.split(",") if a.strip()],
            "friends": [f.strip() for f in friends.split(",") if f.strip()],
            "family": [f.strip() for f in family.split(",") if f.strip()],
            "tags": [t.strip() for t in tags.split(",") if t.strip()]
        }

        new_key = f"{name.lower().replace(' ', '_')}.json"
        try:
            s3.put_object(Bucket=BUCKET_NAME, Key=new_key, Body=json.dumps(data, indent=2))
            st.success(f"Lore for {name} saved to S3!")

            # Trigger backend reload
            reload_resp = requests.post(API_URL.replace("/chat", "/reload_lore"))
            if reload_resp.status_code == 200:
                st.info("Lore reloaded into Blue Bunny’s brain! 🧠")
            else:
                st.warning(f"Saved but reload failed: {reload_resp.text}")

        except Exception as e:
            st.error(f"Failed to save lore to S3: {e}")
