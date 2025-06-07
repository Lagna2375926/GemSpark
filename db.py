import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "ChatApplication"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

users_col = db["users"]
chats_col = db["chats"]
sessions_col = db["sessions"]  # collection to store chat sessions metadata


# --- User Authentication ---

def create_user(username, password):
    """Create new user with hashed password."""
    if users_col.find_one({"username": username}):
        return False  # user exists
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_col.insert_one({"username": username, "password": hashed})
    return True


def authenticate_user(username, password):
    """Verify user credentials."""
    user = users_col.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return str(user["_id"])
    return None


# --- Chat Sessions Management ---

def create_chat_session(user_id, session_name):
    """Create a new chat session for a user."""
    result = sessions_col.insert_one({
        "user_id": ObjectId(user_id),
        "session_name": session_name
    })
    # Also create an empty chat history for this session
    chats_col.insert_one({
        "session_id": result.inserted_id,
        "chat_history": []
    })
    return str(result.inserted_id)


def list_chat_sessions(user_id):
    """List all chat sessions for a user."""
    sessions = sessions_col.find({"user_id": ObjectId(user_id)})
    return [{"session_id": str(s["_id"]), "session_name": s["session_name"]} for s in sessions]


def rename_chat_session(session_id, new_name):
    """Rename a chat session."""
    sessions_col.update_one({"_id": ObjectId(session_id)}, {"$set": {"session_name": new_name}})


def delete_chat_session(session_id):
    """Delete a chat session and its chat history."""
    sessions_col.delete_one({"_id": ObjectId(session_id)})
    chats_col.delete_one({"session_id": ObjectId(session_id)})


# --- Chat History Storage ---

def save_chat_history(session_id, chat_history):
    """
    Save chat history (list of (role, text) tuples) for a session.
    Overwrites the whole chat history for that session.
    """
    # Convert session_id to ObjectId
    chats_col.update_one(
        {"session_id": ObjectId(session_id)},
        {"$set": {"chat_history": chat_history}},
        upsert=True
    )


def get_chat_history(session_id):
    """Retrieve chat history for given session_id."""
    doc = chats_col.find_one({"session_id": ObjectId(session_id)})
    if doc and "chat_history" in doc:
        return doc["chat_history"]
    return []


