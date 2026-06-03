"""Frontend app for the local AI chat interface.

This module builds a Gradio UI that selects chat sessions, loads
conversation history, and sends user messages to the backend chat API.
"""

import gradio as gr
import requests

# Base URL for the backend chat endpoint.
API_URL = "http://127.0.0.1:8000/chat"

# ----- Helper functions -----

def get_chat_list():
    """Return the list of available chat session names from the backend."""
    response = requests.get("http://127.0.0.1:8000/chats")
    return response.json()["chats"]


def chat_with_ai(message, history):
    """Send a user message to the backend and append the assistant response.

    Returns an empty message string plus the updated chat history for the UI.
    """
    try:
        response = requests.post(
            API_URL,
            json={"message": message},
            timeout=120,
        )
        response.raise_for_status()

        ai_response = response.json()["response"]

        # Keep the UI conversation synced with the backend.
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": ai_response})

        return "", history

    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return "", history


def switch_chat(chat_name):
    """Switch to a different chat session and reload its history."""
    requests.post(f"http://127.0.0.1:8000/switch_chat/{chat_name}")

    response = requests.get("http://127.0.0.1:8000/history")
    return response.json()["history"]


def load_chat_history():
    """Load the current chat history from the backend for initial display."""
    try:
        response = requests.get("http://127.0.0.1:8000/history", timeout=10)
        response.raise_for_status()
        history = response.json().get("history", [])
    except Exception:
        history = []

    return history



def create_new_chat():
    """Create a new chat session and refresh the available chat list."""
    response = requests.post("http://127.0.0.1:8000/new_chat")
    current_chat = response.json()["current_chat"]

    chats_response = requests.get("http://127.0.0.1:8000/chats")
    chats = chats_response.json()["chats"]

    return (
        gr.update(
            choices=chats,
            value=current_chat,
        ),
        [],
    )



def rename_chat_ui(chat_name, new_name):
    """Rename the selected chat session and update dropdown state."""
    response = requests.post(
        "http://127.0.0.1:8000/rename_chat",
        json={
            "old_name": chat_name,
            "new_name": new_name,
        },
    )

    result = response.json()

    chats_response = requests.get("http://127.0.0.1:8000/chats")
    chats = chats_response.json()["chats"]
    current_chat = result.get("current_chat", chat_name)

    return (
        gr.update(
            choices=chats,
            value=current_chat,
        ),
        "",
    )




def delete_chat_ui(chat_name):
    """Delete a chat session and load the next available session."""
    response = requests.post(
        "http://127.0.0.1:8000/delete_chat",
        json={"chat_name": chat_name},
    )

    result = response.json()

    chats_response = requests.get("http://127.0.0.1:8000/chats")
    chats = chats_response.json()["chats"]

    history_response = requests.get("http://127.0.0.1:8000/history")
    history = history_response.json()["history"]

    return (
        gr.update(
            choices=chats,
            value=result["current_chat"],
        ),
        history,
    )


# ----- UI definition -----
# Build the Gradio frontend and wire user events to helper functions.

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Local AI Chat")

    new_chat_button = gr.Button("➕ New Chat")

    # rename_button = gr.Button(
    # "✏ Rename Chat"
    # )

    rename_textbox = gr.Textbox(
    label="New Chat Name"
    )

    rename_button = gr.Button(
    "✏ Rename Chat"
    )
    
    delete_button = gr.Button(
    "🗑 Delete Chat"
)

    chat_selector = gr.Dropdown(
        choices=get_chat_list(),
        value=get_chat_list()[0],
        label="Select Chat",
    )

    chatbot = gr.Chatbot(value=load_chat_history(), height=500)

    # Reload the current session history when the selected chat changes.
    chat_selector.change(fn=switch_chat, inputs=[chat_selector], outputs=[chatbot])

    message = gr.Textbox(placeholder="Type your message here...")
    send_button = gr.Button("Send")

    send_button.click(
        fn=chat_with_ai,
        inputs=[message, chatbot],
        outputs=[message, chatbot],
    )

    message.submit(
        fn=chat_with_ai,
        inputs=[message, chatbot],
        outputs=[message, chatbot],
    )

    new_chat_button.click(
    fn=create_new_chat,
    outputs=[
        chat_selector,
        chatbot
    ]
    )

    rename_button.click(
    fn=rename_chat_ui,
    inputs=[
        chat_selector,
        rename_textbox
    ],
    outputs=[
        chat_selector,
        rename_textbox
    ]
    )


    delete_button.click(
    fn=delete_chat_ui,
    inputs=[chat_selector],
    outputs=[
        chat_selector,
        chatbot
    ]
)

demo.launch()


# python frontend/app.py
# http://127.0.0.1:7860