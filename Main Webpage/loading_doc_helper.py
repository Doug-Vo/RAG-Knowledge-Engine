"""
A helper module for the AI Document Workbench application.

This file contains all the core logic for the data ingestion pipeline, including:
- Loading data from PDFs and web pages.
- Checking for duplicate sources in the database.
- Splitting documents into chunks.
- Creating text embeddings and uploading them to a MongoDB Atlas vector store.
"""

import os
import logging
import datetime
import colorama  # type: ignore[import-untyped]
from pymongo import MongoClient

#  IMPORTS FOR LANGCHAIN 
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

#  SETUP COLORED LOGGING 
# This section sets up a custom logger to make terminal output easier to read.
# INFO messages will be green, WARNINGS yellow, and ERRORS bright red.

colorama.init(autoreset=True)
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': colorama.Fore.YELLOW, 'INFO': colorama.Fore.GREEN,
        'DEBUG': colorama.Fore.BLUE, 'CRITICAL': colorama.Fore.YELLOW + colorama.Style.BRIGHT,
        'ERROR': colorama.Fore.RED + colorama.Style.BRIGHT,
    }
    def format(self, record):
        log_message = super().format(record)
        return self.COLORS.get(record.levelname, '') + log_message

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
# Suppress noisy, non-critical warnings from the pypdf library
logging.getLogger("pypdf").setLevel(logging.ERROR)


#  INITIALIZE HEAVY OBJECTS ONCE 

logging.info("Initializing models and clients for helper module...")
MONGO_URI = os.environ.get('MONGO_URI', 'YOUR_MONGO_CONNECTION_STRING')
client: MongoClient = MongoClient(MONGO_URI)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
logging.info("Helper module initialization complete.")

#  DATABASE CONFIGURATION 
DB_NAME = "ai_workbench"
COLLECTION_NAME = "documents"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"


def check_if_source_exists(source_path):
    """
    Checks for duplicates by querying MongoDB to see if any document chunk
    already has this source path in its metadata.
    """
    logging.info(f"Checking for existing source: {source_path}")
    collection = client[DB_NAME][COLLECTION_NAME]
    existing_doc = collection.find_one({"metadata.source": source_path})
    if existing_doc:
        logging.warning(f"Source '{source_path}' already exists in the database.")
        return True
    logging.info(f"Source '{source_path}' is new.")
    return False


def load_pdf(source_path):
    """Loads a PDF file from a local path and returns its content as LangChain Documents."""
    if not source_path.endswith('.pdf'):
        logging.error(f"Error! {source_path} is not a PDF file.")
        return []
    logging.info(f"Loading PDF: {source_path}")
    loader = PyPDFLoader(source_path)
    # Each page of the PDF becomes a separate Document object
    return loader.load()

def load_link(source_url):
    """Loads the text content from a general web page URL."""
    if not source_url.startswith('https://'):
        logging.error(f"Error! {source_url} is not a secure (https) link.")
        return []
    logging.info(f"Loading web page: {source_url}")
    loader = WebBaseLoader(source_url)
    return loader.load()

def split_text(docs):
    """Splits a list of LangChain Documents into smaller chunks."""
    if not docs:
        logging.warning("Received an empty or None list of documents to split.")
        return []
    logging.info(f"Splitting {len(docs)} documents into chunks...")
    # This splitter tries to keep paragraphs together and uses a 150-character overlap
    # to maintain context between chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_docs = text_splitter.split_documents(docs)
    logging.info(f"Created {len(split_docs)} chunks.")
    return split_docs

def embed_and_upload(docs):
    """Creates embeddings for document chunks and uploads them to MongoDB Atlas."""

    if not docs:
        logging.warning("Received no documents to embed and upload. Skipping.")
        return
    logging.info(f"Embedding and uploading {len(docs)} chunks to MongoDB Atlas...")
    collection = client[DB_NAME][COLLECTION_NAME]

    current_time = datetime.datetime.now(datetime.timezone.utc)
    for doc in docs:
        doc.metadata['created_at'] = current_time
        doc.metadata['is_persistent'] = False

    # This LangChain function handles the embedding and upload process in batches.
    MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=embedding_model,
        collection=collection,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )
    logging.info("Upload complete.")