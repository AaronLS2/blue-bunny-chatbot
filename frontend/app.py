import streamlit as st
import requests
import json
from pathlib import Path
import uuid

# Constants
API_URL = "https://blue-bunny-backend.onrender.com/chat"  # Update if backend URL changes
LORE_DIR = Path(__file__).parent / "lore"
LORE_DIR.mkdir(exist_ok=True)

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

    files = list(LORE_DIR.glob("*.json"))

    # Build mapping from display name to filename
    file_map = {
        f.stem.replace("_", " ").title(): f.name for f in files
    }

    # Add the "Add New" option
    options = ["Add New"] + sorted(file_map.keys())
    selected = st.selectbox("Select a character to edit or add a new one:", options)

    if selected == "Add New":
        character = {}
        filename = None
    else:
        # Get the real filename from the map
        selected_filename = file_map[selected]
        filename = LORE_DIR / selected_filename
        with open(filename) as f:
            character = json.load(f)


    name = st.text_input("Name", value=character.get("name", ""))
    species = st.text_input("Species", value=character.get("species", ""))
    location = st.text_input("Location", value=character.get("location", ""))
    personality = st.text_input("Personality", value=character.get("personality", ""))
    backstory = st.text_area("Backstory", value=character.get("backstory", ""))
    abilities = st.text_area("Abilities (comma-separated)", value=", ".join(character.get("abilities", [])))
    friends = st.text_area("Friends (comma-separated)", value=", ".join(character.get("friends", [])))
    family = st.text_area("Family (comma-separated)", value=", ".join(character.get("familiy", [])))
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
            "familiy": [f.strip() for f in family.split(",") if f.strip()],
            "tags": [t.strip() for t in tags.split(",") if t.strip()]
        }

        filename = LORE_DIR / f"{name.lower().replace(' ', '_')}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        st.success(f"Lore for {name} saved!")

        # Reload to ChromaDB (optional: import and call load_lore())
        try:
            import subprocess
            subprocess.run(["python3", "lore_loader.py"], check=True)
            st.info("Lore reloaded into Blue Bunny's brain!")
        except Exception as e:
            st.error(f"Failed to reload lore: {e}")
