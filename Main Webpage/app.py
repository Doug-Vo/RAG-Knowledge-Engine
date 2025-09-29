import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import logging
from langchain_openai import ChatOpenAI

# --- IMPORT HELPER FUNCTION ---
# Imports all the necessary data processing functions and global variables
from loading_doc_helper import (
    load_pdf, load_youtube, load_link, 
    split_text, embed_and_upload,
    check_if_source_exists,
    DB_NAME, COLLECTION_NAME, embedding_model, client, ATLAS_VECTOR_SEARCH_INDEX_NAME
)

# Imports the necessary LangChain components for building the RAG chain.
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

# --- QA SET UP ---
# This section configures and initializes the RAG (Retrieval-Augmented Generation)
# chain. These objects are created once when the server starts for efficiency.

# Gets the specific MongoDB collection object from the client that was initialized in the helper file.
collection = client[DB_NAME][COLLECTION_NAME]

# Initializes the Large Language Model (LLM) from OpenAI that will generate the final answers.
# It uses the OPENAI_API_KEY environment variable automatically.
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Initializes the vector store object, which connects to our MongoDB Atlas database.
# This object knows how to use the embedding model to search for relevant documents.
vector_store = MongoDBAtlasVectorSearch(
    collection= collection, 
    embedding= embedding_model,
    index_name= ATLAS_VECTOR_SEARCH_INDEX_NAME
)
logging.info("RAG chain is ready.")

# Creates the final RetrievalQA chain. This object ties everything together:
# it takes a question, uses the retriever to find documents, and sends them to the LLM.
qa = RetrievalQA.from_chain_type(
    llm = llm,
    retriever = vector_store.as_retriever(),
    chain_type = "map_reduce",
    return_source_documents = True # Instructs the chain to return which documents it used
)


# --- FLASK APP SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 
# Configures a temporary folder to store PDF files during the upload process.
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- FLASK WEB ROUTES ---
# Main Route & QA Route
@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handles both displaying the main page (GET) and processing Q&A form submissions (POST).
    """
    answer = None
    question = None
    source_documents = None

    # This block only runs when the user submits the "Ask a Question" form.
    if request.method == 'POST':
        question = request.form.get('question')
        logging.info(f"QA chain for {question}")
        
        # Proceeds only if the user actually typed a question.
        if question:
            try:
                result = qa.invoke({"query": question})
                answer = result["result"]
                
                logging.info(f"Received the answer: {answer}")
                # If the chain returned the source documents, this extracts their names.
                if result.get("source_documents"):
                    raw_sources = [doc.metadata.get('source', 'Unknown') for doc in result["source_documents"]]
                    # Creates a list of unique source names.
                    source_documents = list(set(raw_sources))
                
            except Exception as e:
                logging.error(f"UNABLE TO QA {question}: {e}")
                answer = "Sorry something broke!!"
    
    return render_template('index.html', 
                           answer = answer,
                           question =  question,
                           source_documents = source_documents)


# Ingest Data Route
@app.route('/ingest', methods=['POST'])
def ingest():
    """Handles the document ingestion pipeline when the 'Add Knowledge' form is submitted."""
    source_path = None
    source_name = None

    # Determines the source: either a PDF file or a URL from the form.
    if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
        file = request.files['pdf_file']
        source_path = secure_filename(file.filename)
        source_name = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
    elif 'source_url' in request.form and request.form['source_url'].strip():
        source_path = request.form['source_url'].strip()
        source_name = source_path
    
    # If no valid source was provided, show a warning to the user.
    if not source_path:
        flash("No valid input provided. Please upload a PDF or enter a URL.", "warning")
        return redirect(url_for('home'))

    # Checks if this exact source (filename or URL) already exists in the database.
    logging.warning(f"CHECKING:-----{source_name}")
    if check_if_source_exists(source_name):
        flash(f"KNOWLEDGE ALREADY EXISTS: '{source_name}' has already been ingested.", "warning")
        return redirect(url_for('home'))

    # If it's a new source, proceed with the ingestion pipeline.
    source_data = None
    try:
        # Calls the appropriate loader function from the helper file based on the source type.
        if source_path.endswith('.pdf'):
            file = request.files['pdf_file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
            file.save(filepath)
            source_data = load_pdf(filepath)
            os.remove(filepath) # Cleans up the temporary file
        elif 'youtube.com' in source_path or 'youtu.be' in source_path:
            source_data = load_youtube(source_path)
        else:
            source_data = load_link(source_path)
        
        # The main ingestion pipeline: splits the loaded data into chunks and uploads them.
        if source_data:
            chunks = split_text(source_data)
            embed_and_upload(chunks)
            flash(f"KNOWLEDGE UPLOADED: Successfully ingested '{source_path}'.", "success")
        else:
            raise Exception("Failed to load data from the source.")

    except Exception as e:
        logging.error(f"Ingestion pipeline failed for '{source_path}': {e}")
        flash(f"UNABLE TO UPLOAD KNOWLEDGE: An error occurred with '{source_path}'.", "error")

    return redirect(url_for('home'))

if __name__ == '__main__':
    # 'debug=True' enables auto-reloading when save  the file
    app.run(debug=True)