# RAG Chatbot — Streamlit + ChromaDB + Claude

A complete beginner-friendly RAG chatbot. Ask questions and get answers from your own documents.

## How to run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open in browser
Streamlit will open http://localhost:8501 automatically.

### 4. Enter your API key
Paste your Anthropic API key in the sidebar (get one at console.anthropic.com).

---

## How to add your own documents

In `app.py`, find the `sample_docs` list inside `load_db()` and replace it with your own content:

```python
sample_docs = [
    "Your first document text here...",
    "Your second document text here...",
    # add as many as you need
]
```

For loading real PDF files, add `pypdf` to requirements.txt and use:

```python
from pypdf import PdfReader

def load_pdf(path):
    reader = PdfReader(path)
    return " ".join(page.extract_text() for page in reader.pages)
```

---

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository
2. Go to share.streamlit.io
3. Connect your GitHub repo
4. Add your ANTHROPIC_API_KEY in the Secrets panel
5. In app.py, change the api_key line to: `api_key = st.secrets["ANTHROPIC_API_KEY"]`
6. Deploy — get a shareable URL!

---

## What each file does

| File | Purpose |
|------|---------|
| app.py | The entire app — UI + RAG logic |
| requirements.txt | Python packages to install |
| README.md | This file |
