# Local AI Chat App

This repository contains a local AI chat application built with a FastAPI backend and a Gradio frontend. It provides persistent chat sessions, supports creating, renaming, and deleting chats, and forwards user messages to an Ollama model for AI responses.

## Project Overview

- **Backend:** `backend/main.py`
  - FastAPI application
  - Stores chat sessions as JSON files in `conversations/`
  - Exposes endpoints for chat history, chat switching, new chat creation, rename, delete, and message processing
  - Sends messages to a local Ollama instance at `http://localhost:11434/api/chat`

- **Frontend:** `frontend/app.py`
  - Gradio UI for interacting with the chat system
  - Displays chat history in a chat widget
  - Supports selecting chat sessions, creating new chats, renaming chats, deleting chats, and sending messages

- **Chat storage:** `conversations/`
  - Each chat session is stored as its own JSON file, named like `chat_1.json`, `chat_2.json`, etc.

## Key Features

- Persistent chat sessions saved to disk
- Ability to switch between chat sessions
- Create new chat sessions dynamically
- Rename chat sessions
- Delete chat sessions
- Send messages to a local Ollama model and show responses in the UI

## Requirements

The app depends on the Python packages listed in `requirements.txt`, including:

- `fastapi`
- `uvicorn`
- `gradio`
- `requests`
- `pydantic`
- `anyio`
- `starlette`

The project also requires:

- A local Ollama installation
- A local Ollama-compatible LLM model loaded, such as `smollm:latest`

Additional dependencies include the packages required by Gradio, requests, and the backend API.

## Setup and Run

1. Create and activate a Python virtual environment in the project root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running locally, and that a model such as `smollm:latest` is loaded.

4. Start the backend API.

```powershell
uvicorn backend.main:app --reload
```

5. Start the frontend UI.

```powershell
python frontend/app.py
```

5. Open the Gradio UI at the address printed by the frontend, usually `http://127.0.0.1:7860`.

## Backend API Details

The backend exposes the following endpoints:

- `GET /` - health check
- `GET /history` - returns the current chat history
- `GET /chats` - returns the list of available chat session names
- `POST /switch_chat/{chat_name}` - switch active chat session and reload history
- `POST /new_chat` - create a new chat session and switch to it
- `POST /rename_chat` - rename an existing chat session
- `POST /delete_chat` - delete an existing chat session
- `POST /chat` - send a new message to the AI model and return the response

## Notes

- This app expects a local Ollama model API to be available at `http://localhost:11434/api/chat`.
- Chat sessions are stored in the `conversations/` folder. Each chat file is a JSON array of messages.
- The backend uses `CURRENT_CHAT` to track the active chat session in memory, and reloads the corresponding JSON file on switch.

## Project Structure

```
ai-chat-app/
├── backend/
│   ├── main.py
│   ├── chat_logs.txt
│   └── conversation_history.json
├── conversations/
│   ├── chat_2.json
│   ├── chat_4.json
│   └── notes.json
├── frontend/
│   └── app.py
├── requirements.txt
└── README.md
```

## Troubleshooting

- If the frontend raises errors while renaming or deleting chats, make sure the backend is running and the `conversations/` folder exists.
- If the AI response call fails, verify that Ollama is running on `localhost:11434`, and that a local model such as `smollm:latest` is loaded and available.
- If the `requirements.txt` file is encoding-sensitive, use the proper environment and a UTF-16-capable editor to inspect it.


