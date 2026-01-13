# AI Document Workbench (RAG Knowledge Engine)

 **Retrieval Augmented Generation (RAG)** application that allows users to "chat" with their documents. It uses a **Hybrid Knowledge Base** architecture, supporting both permanent organizational documents and temporary user uploads that auto-expire.

## Live website: https://rag-application.azurewebsites.net

## ✨ Features

* **Hybrid Database:**
    * **Permanent Docs:** Core documents (manuals, policies) stay forever.
    * **Temporary Uploads:** User-uploaded files are **automatically deleted after 1 hour** to maintain hygiene.
* **Multi-Source Ingestion:**
    * **PDFs:** Upload local files.
    * **Web Links:** Scrapes and indexes text from URLs.
    * **YouTube:** Downloads transcripts. **Auto-translates** non-English captions to English before indexing.
* **Modern AI Stack:**
    * **LLM:** OpenAI GPT-4o-mini (Cost-effective & fast).
    * **Vector Store:** MongoDB Atlas Vector Search.
    * **Embeddings:** OpenAI `text-embedding-3-small` (1536 Dimensions).
    * **Framework:** LangChain v0.3 (LCEL Architecture).

## 🔧 Technical Pipeline

1.  **Ingestion:** `LangChain Community Loaders` (PyPDF, WebBase) & `pytubefix` (YouTube).
2.  **Processing:** Text is split into chunks (`RecursiveCharacterTextSplitter`) and translated if necessary (`deep-translator`).
3.  **Storage:** Embeddings are generated via `text-embedding-3-small` and stored in **MongoDB Atlas**.
4.  **Retrieval:** `MongoDBAtlasVectorSearch` performs cosine similarity search.
5.  **Generation:** `LangChain LCEL` pipes retrieved context + query to `OpenAI GPT-4o-mini`.

## 📚 Tech Stack Details

* **Frontend:** HTML5, TailwindCSS, Vanilla JS
* **Backend:** Flask (Python)
* **AI Orchestration:** LangChain Core (Runnables/LCEL)
* **Translation:** Deep Translator 

---
---
# Getting Started

### Prerequisites

* [Python 3.10+](https://www.python.org/)
* [MongoDB Atlas Account](https://www.mongodb.com/cloud/atlas) (Free tier works)
* [OpenAI API Key](https://platform.openai.com/)

### Installation

1.  **Clone the repository**
    ```sh
    git clone [https://github.com/Doug-Vo/RAG-Knowledge-Engine.git](https://github.com/Doug-Vo/RAG-Knowledge-Engine.git)
    cd `Main-Webpage`
    ```

2.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**
    Create a `.env` file in the `Main Webpage` directory:
    ```env
    MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
    OPENAI_API_KEY=sk-proj-....
    SECRET_KEY=your_secret_key_for_flask_sessions
    ```

4.  **Configure MongoDB Atlas**
    * Create a Database: `ai_workbench`
    * Create a Collection: `documents`
    * **Create a Vector Search Index** (JSON Editor):
        ```json
        {
            "fields": [
                {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1536,
                "similarity": "cosine"
                }
            ]
        }
        ```

### Usage

1.  **Run the Application**
    ```sh
    python app.py
    ```
2.  Open your browser to `http://127.0.0.1:5000`.
3.  **Ingest:** Go to the "Add Knowledge" tab to upload a PDF or paste a YouTube URL.
4.  **Query:** Go to "Ask a Question" to chat with your data.

## ⚙️ Environment Variables Reference

| Variable | Description | Required? |
| :--- | :--- | :--- |
| `MONGO_URI` | Your full MongoDB Atlas connection string. | **Yes** |
| `OPENAI_API_KEY` | Your OpenAI API Key for the LLM. | **Yes** |
| `SECRET_KEY` | A random string for Flask session | **No** 



---
*Created by Doug Vo*