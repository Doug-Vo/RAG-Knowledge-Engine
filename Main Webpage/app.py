import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_talisman import Talisman


#  LANGCHAIN IMPORTS 
from langchain_openai import ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

#  HELPER IMPORTS 
from loading_doc_helper import (
    load_pdf, load_youtube, load_link, 
    split_text, embed_and_upload,
    check_if_source_exists,
    DB_NAME, COLLECTION_NAME, embedding_model, client, ATLAS_VECTOR_SEARCH_INDEX_NAME
)

# Load environment variables (API keys)
load_dotenv()

#  LOGGING SETUP 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#  CONFIGURATION 
collection = client[DB_NAME][COLLECTION_NAME]

if not os.environ.get("OPENAI_API_KEY"):
    logging.warning("OPENAI_API_KEY not found! RAG will fail.")

# 1. Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Updated to latest cost-effective model
    temperature=0,
)

# 2. Initialize Vector Store
vector_store = MongoDBAtlasVectorSearch(
    collection=collection, 
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
)
logging.info("RAG chain is ready.")

#  RAG CHAIN SETUP (LCEL) 

#  Prompt
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the following context to answer the user's question. If you don't know, say you don't know.\n\n{context}"),
    ("human", "{input}"),
])

retriever = vector_store.as_retriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# QA Chain
qa_chain = (
    RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
    | chat_prompt
    | llm
    | StrOutputParser()
)

# Final Chain (Parallel Retrieval)
# This ensures we get both the Answer (str) and the Context (list of docs)
rag_chain = RunnableParallel(
    {"context": retriever, "input": RunnablePassthrough()}
).assign(answer=qa_chain)


#  FLASK APP SETUP 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_only') # Use env var for production

talisman = Talisman(app, content_security_policy = None, force_https = True)

# SET UP COOKIE SESSION

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#  ROUTES 

@app.route('/', methods=['GET', 'POST'])
def home():
    answer = None
    question = None
    source_documents = []

    active_tab = 'about'

    if request.args.get('tab'):
        active_tab = request.args.get('tab')

    

    if request.method == 'POST':
        active_tab = 'query'
        question = request.form.get('question')
        logging.info(f"QA chain for: {question}")
        
        if question:
            try:
                # Invoke the chain
                result = rag_chain.invoke(question)
                
                # Extract Answer
                answer = result["answer"]
                logging.info(f"Answer generated.")

                # Extract Documents
                retrieved_docs = result.get("context", [])
                logging.info(f"Retrieved {len(retrieved_docs)} documents.")

                if not retrieved_docs:
                    source_documents = ["No relevant documents found in knowledge base."]
                else:
                    # Clean up source names for display
                    raw_sources = []
                    for doc in retrieved_docs:
                        url = doc.metadata.get('source', 'Unknown Source')
                        title = doc.metadata.get('title')
                        
                        # Fallback for missing titles
                        if not title and url != 'Unknown Source':
                            title = os.path.basename(url)
                        if not title:
                            title = "Document Fragment"

                        raw_sources.append(f"{title} ({url})")
                    
                    source_documents = list(set(raw_sources))
                
            except Exception as e:
                logging.error(f"Error during QA: {e}", exc_info=True)
                answer = "Sorry, something went wrong while processing your question."
    
    return render_template('index.html', 
                           answer=answer,
                           question=question,
                           source_documents=source_documents,
                           active_tab = active_tab)


@app.route('/ingest', methods=['POST'])
def ingest():
    source_path = None
    source_name = None

    # Handle PDF Upload
    if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
        file = request.files['pdf_file']
        source_path = secure_filename(file.filename)
        source_name = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
    
    # Handle URL Input
    elif 'source_url' in request.form and request.form['source_url'].strip():
        source_path = request.form['source_url'].strip()
        source_name = source_path
    
    if not source_path:
        flash("No valid input provided.", "warning")
        return redirect(url_for('home'))

    logging.info(f"Processing ingestion for: {source_name}")

    # Check for duplicates
    if check_if_source_exists(source_name):
        flash(f"Already exists: '{source_name}'", "warning")
        return redirect(url_for('home'))

    try:
        source_data = None
        # PDF Logic
        if source_path.endswith('.pdf'):
            file = request.files['pdf_file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
            file.save(filepath)
            try:
                source_data = load_pdf(filepath)
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath) # Ensure cleanup even if load fails
        
        # YouTube Logic
        elif 'youtube.com' in source_path or 'youtu.be' in source_path:
            source_data = load_youtube(source_path)
        
        # Web Link Logic
        else:
            source_data = load_link(source_path)
        
        # Split and Upload
        if source_data:
            chunks = split_text(source_data)
            embed_and_upload(chunks)
            flash(f"Successfully ingested '{source_path}'.", "success")
        else:
            raise Exception("No text could be extracted.")

    except Exception as e:
        logging.error(f"Ingestion failed: {e}", exc_info=True)
        flash(f"Error ingesting '{source_path}': {str(e)}", "error")

    return redirect(url_for('home', tab= 'ingest'))

# Health Check for Azure
@app.route('/healthz', methods=['GET'])
@talisman(force_https=False)
def health_check():
    try:
        if 'client' not in globals() or client is None:
            raise Exception('database client not configured')

        # Ping MongoDB 
        result = client.admin.command('ping')
        ok = None
        if isinstance(result, dict):
            ok = result.get('ok')

        if ok is not None and float(ok) == 1.0:
            return jsonify(status="healthy", database="connected"), 200
        else:
            logging.error(f"Health ping returned unexpected value: {result}")
            return jsonify(status="unhealthy", reason="ping_failed", detail=result), 500
        
    except Exception as e:
        logging.error(f"Health check failed: {e}", exc_info=True)
        return jsonify(status="unhealthy", reason=str(e)), 500

if __name__ == '__main__':
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)