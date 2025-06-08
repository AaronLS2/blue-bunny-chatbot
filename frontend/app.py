import streamlit as st
import requests

st.set_page_config(page_title="Blue Bunny Chat", page_icon="🐰", layout="centered")

st.title("🐰 Blue Bunny Chatbot")
st.caption("Chat with the legendary stuffed hero of Stuffed Animal World (SAW)")

# Add a link to the lore editor in the sidebar
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown("[Edit Lore 📝](http://localhost:8502)", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to send message to backend
def ask_blue_bunny(message):
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": message},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["reply"]
        else:
            return "Oops! Blue Bunny is napping. Try again soon."
    except Exception as e:
        return f"Error: {e}"

# Input form (prevents infinite rerun)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Ask me anything about SAW...", key="user_input_input")
    submitted = st.form_submit_button("Send")

# Handle form submission
if submitted and user_input:
    st.session_state.messages.insert(0, {"role": "user", "content": user_input})
    reply = ask_blue_bunny(user_input)
    st.session_state.messages.insert(0, {"role": "blue_bunny", "content": reply})
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Blue Bunny 🐰:** {msg['content']}")
