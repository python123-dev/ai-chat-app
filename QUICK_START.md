## Quick Start

### 1. Clone Repository

```
git clone 
cd ai-chat-app
```

### 2. Create Virtual Environment

```
python -m venv venv
```

### 3. Activate Virtual Environment
Windows:

```
venv\Scripts\activate
```
Linux/Mac:

```
source venv/bin/activate
```

### 4. Install Dependencies

```
pip install -r requirements.txt
```

### 5. Pull the Model (First Time Only)

```
ollama pull smollm
```

### 6. Start FastAPI Backend

```
uvicorn backend.main:app --reload
```

### 7. Start Gradio Frontend
Open a new terminal:

```
python frontend/app.py
```

### 8. Open the Application

```
http://127.0.0.1:7860
```
