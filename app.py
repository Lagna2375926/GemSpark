import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from db import (
    create_user,
    authenticate_user,
    create_chat_session,
    list_chat_sessions,
    rename_chat_session,
    delete_chat_session,
    save_chat_history,
    get_chat_history,
)
from bson.objectid import ObjectId

# Load env variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Streamlit page config (MUST be first command)
st.set_page_config(page_title="GemSpark", page_icon="🤖", layout="wide")


def format_history_for_gemini(chat_history):
    """
    Convert stored chat history (list of (role, text)) into Gemini API format:
    [{'role': 'user', 'parts': ['message']}, ...]
    """
    formatted = []
    for role, text in chat_history:
        # Gemini expects 'model' instead of 'assistant'
        role_converted = "model" if role == "assistant" else "user"
        formatted.append({"role": role_converted, "parts": [text]})
    return formatted




def get_gemini_response(question, chat_history):
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(question, stream=True)
    return response



# --- Authentication UI ---
if "user_id" not in st.session_state:
    st.title("Login or Register")
    choice = st.radio("Choose Action", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button(choice):
        if not username or not password:
            st.error("Please enter username and password")
        elif choice == "Register":
            if create_user(username, password):
                st.success("User created! Please login.")
            else:
                st.error("Username already exists.")
        else:  # Login
            user_id = authenticate_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")
    st.stop()

# --- Main app after login ---
user_id = st.session_state.user_id
username = st.session_state.username

st.sidebar.title(f"GemSpark — {username}")

# List chat sessions for user
sessions = list_chat_sessions(user_id)

# Build dict {session_name: session_id} for dropdown
session_options = {s["session_name"]: s["session_id"] for s in sessions}

# Initialize selected session in session_state if not set
if "selected_session_id" not in st.session_state or "selected_session_name" not in st.session_state:
    if sessions:
        st.session_state.selected_session_id = sessions[0]["session_id"]
        st.session_state.selected_session_name = sessions[0]["session_name"]
    else:
        new_id = create_chat_session(user_id, "First Chat")
        st.session_state.selected_session_id = new_id
        st.session_state.selected_session_name = "First Chat"
        sessions = list_chat_sessions(user_id)
        session_options = {s["session_name"]: s["session_id"] for s in sessions}

# Prepare options list for selectbox
session_names = list(session_options.keys())
# Find current index safely
try:
    current_index = session_names.index(st.session_state.selected_session_name)
except ValueError:
    current_index = 0

# Sidebar selectbox for sessions
selected_session_name = st.sidebar.selectbox(
    "Select Chat Session",
    options=session_names,
    index=current_index,
)

# Update session_state if user changed selection
if selected_session_name != st.session_state.selected_session_name:
    st.session_state.selected_session_name = selected_session_name
    st.session_state.selected_session_id = session_options[selected_session_name]
    # Clear chat history so it reloads for new session
    if "chat_history" in st.session_state:
        del st.session_state["chat_history"]

# Sidebar new chat button
if st.sidebar.button("➕ New Chat"):
    new_chat_name = f"Chat {len(sessions) + 1}"
    new_session_id = create_chat_session(user_id, new_chat_name)
    st.session_state.selected_session_id = new_session_id
    st.session_state.selected_session_name = new_chat_name
    if "chat_history" in st.session_state:
        del st.session_state["chat_history"]
    st.rerun()

# Sidebar rename current chat session
new_name = st.sidebar.text_input("Rename current chat", value=st.session_state.selected_session_name)
if new_name != st.session_state.selected_session_name:
    if st.sidebar.button("Rename"):
        rename_chat_session(st.session_state.selected_session_id, new_name)
        st.session_state.selected_session_name = new_name
        st.rerun()

# Sidebar delete current chat session
if st.sidebar.button("🗑️ Delete current chat"):
    delete_chat_session(st.session_state.selected_session_id)
    # Refresh sessions
    sessions = list_chat_sessions(user_id)
    session_options = {s["session_name"]: s["session_id"] for s in sessions}
    if sessions:
        st.session_state.selected_session_id = sessions[0]["session_id"]
        st.session_state.selected_session_name = sessions[0]["session_name"]
    else:
        new_id = create_chat_session(user_id, "First Chat")
        st.session_state.selected_session_id = new_id
        st.session_state.selected_session_name = "First Chat"
    if "chat_history" in st.session_state:
        del st.session_state["chat_history"]
    st.rerun()

# Logout button
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# Page title with current session name
st.title(f"🤖 GemSpark Chat — {st.session_state.selected_session_name}")

# Load chat history if not in session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = get_chat_history(st.session_state.selected_session_id)

# Display chat messages
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# Chat input box
if prompt := st.chat_input("Ask your question here..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.chat_history.append(("user", prompt))

    # Format last 10 messages for Gemini
    formatted_history = format_history_for_gemini(st.session_state.chat_history[-10:])

    with st.spinner("Generating response..."):
        response_chunks = get_gemini_response(prompt, formatted_history)
        ai_response = ""
        for chunk in response_chunks:
            ai_response += chunk.text

    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.chat_history.append(("assistant", ai_response))

    # Save updated chat history in DB
    save_chat_history(st.session_state.selected_session_id, st.session_state.chat_history)

