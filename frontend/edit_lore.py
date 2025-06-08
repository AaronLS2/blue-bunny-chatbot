import streamlit as st
import json
import os
from pathlib import Path
import sys

# 📁 Ensure we can import from root dir
sys.path.append(str(Path(__file__).resolve().parent.parent))
from lore_loader import load_lore

# 📁 Set lore directory (root level)
LORE_DIR = Path(__file__).resolve().parent.parent / "lore"

# 🧾 Load existing character files
def load_existing_characters():
    characters = {}
    if not LORE_DIR.exists():
        return characters
    for file in LORE_DIR.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            characters[data["name"]] = data
    return characters

st.set_page_config(page_title="Edit SAW Lore", page_icon="📝")
st.title("📝 SAW Lore Editor")

characters = load_existing_characters()
names = ["(New Character)"] + sorted(characters.keys())
selected = st.selectbox("Select Character to Edit", names)

if selected != "(New Character)":
    char = characters[selected]
else:
    char = {
        "name": "",
        "species": "",
        "location": "",
        "personality": "",
        "backstory": "",
        "abilities": [],
        "friends": [],
        "family": [],
        "tags": []
    }

# ✍️ Input form
name = st.text_input("Name", value=char["name"])
species = st.text_input("Species", value=char["species"])
location = st.text_input("Location", value=char["location"])
personality = st.text_area("Personality", value=char["personality"])
backstory = st.text_area("Backstory", value=char["backstory"])
abilities = st.text_input("Abilities (comma-separated)", value=", ".join(char["abilities"]))
friends = st.text_input("Friends (comma-separated)", value=", ".join(char["friends"]))
family = st.text_input("Family (comma-separated)", value=", ".join(char["family"]))
tags = st.text_input("Tags (comma-separated)", value=", ".join(char["tags"]))

# 💾 Save character
if st.button("💾 Save Character"):
    if not name.strip():
        st.error("Name is required.")
    else:
        filename = name.strip().lower().replace(" ", "_") + ".json"
        LORE_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "name": name.strip(),
            "species": species.strip(),
            "location": location.strip(),
            "personality": personality.strip(),
            "backstory": backstory.strip(),
            "abilities": [a.strip() for a in abilities.split(",") if a.strip()],
            "friends": [f.strip() for f in friends.split(",") if f.strip()],
            "family": [r.strip() for r in family.split(",") if r.strip()],
            "tags": [t.strip() for t in tags.split(",") if t.strip()]
        }

        with open(LORE_DIR / filename, "w") as f:
            json.dump(data, f, indent=2)

        load_lore()  # 🧠 Update ChromaDB
        st.success(f"✅ {name} saved and lore reloaded!")

# 🔙 Link back to chatbot
st.sidebar.markdown("[⬅️ Back to Chatbot](http://localhost:8501)", unsafe_allow_html=True)
