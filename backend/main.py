"""Backend API for the local AI chat application.

This module exposes endpoints for chat history, switching chat sessions,
and forwarding user messages to the local Ollama model.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import requests
from datetime import datetime
import json
import os

app = FastAPI()

# ----- Configuration -----
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "smollm:latest"
MAX_MESSAGES = 6

SYSTEM_PROMPT = """
You are a helpful AI assistant.

Rules:
- Give concise answers in 10 words or less.
- Stay focused on the user's questions.
- Do not invent facts.
- If you don't know something, say so.
"""

# The currently selected chat session file name.
CURRENT_CHAT = "chat_1"


def get_chat_file():
    """Build the file path for the current chat session."""
    return f"conversations/{CURRENT_CHAT}.json"


def load_history():
    """Load the current chat session history from disk.

    Returns an empty list if the file is missing or invalid.
    """
    if os.path.exists(get_chat_file()):
        with open(get_chat_file(), "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    return []


def save_history():
    """Persist the current conversation history back to disk."""
    with open(get_chat_file(), "w", encoding="utf-8") as f:
        json.dump(
            conversation_history,
            f,
            indent=4,
            ensure_ascii=False,
        )


# Load the last saved history when the app starts.
conversation_history = load_history()
print(f"Loaded {len(conversation_history)} messages from history.")


# ----- Request models -----
class ChatRequest(BaseModel):
    message: str


# ----- Logging helpers -----
def write_log(user_message, ai_response):
    """Append a simple text log entry for each user interaction."""
    with open("backend/chat_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\n")
        f.write(f"USER: {user_message}\n")
        f.write(f"AI: {ai_response}\n")
        f.write("-" * 50 + "\n")


class RenameChatRequest(BaseModel):
    old_name: str
    new_name: str


class DeleteChatRequest(BaseModel):
    chat_name: str


# ----- API endpoints -----
@app.get("/")
def home():
    """Health check endpoint for the backend service."""
    return {"status": "running"}


@app.get("/history")
def get_history():
    """Return the message history for the currently selected chat session."""
    return {"history": conversation_history}


@app.post("/switch_chat/{chat_name}")
def switch_chat(chat_name: str):
    """Switch the active chat session and reload its stored history."""
    global CURRENT_CHAT
    global conversation_history

    CURRENT_CHAT = chat_name
    conversation_history = load_history()

    return {
        "current_chat": CURRENT_CHAT,
        "messages": len(conversation_history),
    }


@app.post("/chat")
def chat(request: ChatRequest):
    """Handle a new user message and forward it to the Ollama model."""
    conversation_history.append({"role": "user", "content": request.message})

    messages_to_send = conversation_history[-MAX_MESSAGES:]
    print(f"\nTotal History: {len(conversation_history)}")
    print(f"Messages Sent To Model: {len(messages_to_send)}")

    final_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ] + messages_to_send

    payload = {
        "model": MODEL_NAME,
        "messages": final_messages,
        "stream": False,
    }

    response = requests.post(OLLAMA_URL, json=payload)
    result = response.json()
    ai_response = result["message"]["content"]

    conversation_history.append({"role": "assistant", "content": ai_response})
    save_history()
    write_log(request.message, ai_response)

    return {"response": ai_response}


@app.get("/chats")
def get_chats():
    """Return the list of available chat session files."""
    files = []
    for file in os.listdir("conversations"):
        if file.endswith(".json"):
            files.append(file.replace(".json", ""))

    return {"chats": files}



@app.post("/new_chat")
def new_chat():

    global CURRENT_CHAT
    global conversation_history

    chat_files = []

    for file in os.listdir("conversations"):

        if file.endswith(".json"):

            chat_files.append(file)

    next_number = len(chat_files) + 1

    chat_name = f"chat_{next_number}"

    with open(
        f"conversations/{chat_name}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump([], f)

    CURRENT_CHAT = chat_name

    conversation_history = []

    return {
        "current_chat": chat_name
    }


@app.post("/rename_chat")
def rename_chat(request: RenameChatRequest):

    global CURRENT_CHAT

    old_file = f"conversations/{request.old_name}.json"
    new_file = f"conversations/{request.new_name}.json"

    if not os.path.exists(old_file):

        return {
            "success": False,
            "message": "Chat not found"
        }

    if os.path.exists(new_file):

        return {
            "success": False,
            "message": "Chat name already exists"
        }

    os.rename(
        old_file,
        new_file
    )

    if CURRENT_CHAT == request.old_name:

        CURRENT_CHAT = request.new_name

    return {
        "success": True,
        "current_chat": CURRENT_CHAT
    }



@app.post("/delete_chat")
def delete_chat(request: DeleteChatRequest):

    global CURRENT_CHAT
    global conversation_history

    chat_files = []

    for file in os.listdir("conversations"):

        if file.endswith(".json"):
            chat_files.append(file)

    # Prevent deleting the last remaining chat

    if len(chat_files) <= 1:

        return {
            "success": False,
            "message": "Cannot delete the last chat"
        }

    file_to_delete = f"conversations/{request.chat_name}.json"

    if not os.path.exists(file_to_delete):

        return {
            "success": False,
            "message": "Chat not found"
        }

    os.remove(file_to_delete)

    # Get remaining chats

    remaining_chats = []

    for file in os.listdir("conversations"):

        if file.endswith(".json"):

            remaining_chats.append(
                file.replace(".json", "")
            )

    remaining_chats.sort()

    # Switch to first remaining chat

    CURRENT_CHAT = remaining_chats[0]

    conversation_history = load_history()

    return {
        "success": True,
        "current_chat": CURRENT_CHAT
    }


# Run with: uvicorn backend.main:app --reload