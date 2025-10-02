# RAG KNOWLEDGE ENGINE

My startup project on using **RAG (Retrieval Augmented Generation)** pipeline along with MongoDB to answer question based on the documents ingested

## Extra Plugs:
- Video 
- [Info Slides](https://docs.google.com/presentation/d/1gBh9gEL8tzIML4RIR9M011QN1lgIxafQ/edit?usp=sharing&ouid=101357731019395598793&rtpof=true&sd=true)

## ✨ Features

* Connects securely to a MongoDB database.
* Ingesting multiple source (PDFs, link, youtube)
* QA bot

## 🔧 Pipeline
- [LangChain - RetrievalQA](https://python.langchain.com/api_reference/langchain/chains/langchain.chains.retrieval_qa.base.RetrievalQA.html)
- [HuggingFace Embedding Model - all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [OpenAI API](https://platform.openai.com/docs/overview) (Sharing pipeline with LangChain)


### Prerequisites

You will need the following software installed on your machine:

* [Python](https://www.python.org/) (v3.8 or later is recommended)
* [Pip](https://pip.pypa.io/en/stable/installation/) (which is typically included with Python)
* [Git](https://git-scm.com/)
* A MongoDB database instance. You can create a free one on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

### Installation

1.  **Clone the repository**
    ```sh
    git clone https://github.com/Doug-Vo/RAG-Knowledge-Engine.git
    ```

2.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```




## ⚙️ Environment Variables

| Variable         | Description                                                                                                                              | Example                                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `MONGODB_URI`    | **Required.** Your full MongoDB connection string, including your username, password, and database name. This is crucial for connecting to the database. | `mongodb+srv://<user>:<password>@cluster-name.mongodb.net/myDatabase?retryWrites=true&w=majority` |
| `OPENAI_API_KEY`      | **Required.** We need OpenAI key for this project                                                                          | 

---
