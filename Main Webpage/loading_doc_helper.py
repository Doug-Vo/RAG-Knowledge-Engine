import os
import logging
import time
import asyncio
import colorama
from pymongo import MongoClient
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.docstore.document import Document
from pytubefix import YouTube
from googletrans import Translator

# --- SETUP COLORED LOGGING ---
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
logging.getLogger("pypdf").setLevel(logging.ERROR)

# --- INITIALIZE HEAVY OBJECTS ONCE ---
logging.info("Initializing models and clients for helper module...")
MONGO_URI = os.environ.get('MONGO_URI', 'YOUR_MONGO_CONNECTION_STRING')
client = MongoClient(MONGO_URI)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
translator = Translator()
logging.info("Helper module initialization complete.")

# --- DATABASE CONFIGURATION ---
DB_NAME = "ai_workbench"
COLLECTION_NAME = "documents"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"

# --- HELPER FUNCTIONS ---
def clean_srt_captions(srt_text):
    lines = srt_text.splitlines()
    clean_lines = []
    for line in lines:
        if line.strip() and not line.strip().isdigit() and '-->' not in line:
            clean_lines.append(line.strip())
    return " ".join(clean_lines)

def check_if_source_exists(source_path):
    """
    Checks the MongoDB collection to see if a document with the given
    source name already exists in the metadata.
    """
    logging.info(f"Checking for existing source: {source_path}")
    collection = client[DB_NAME][COLLECTION_NAME]
    existing_doc = collection.find_one({"source": source_path})
    if existing_doc:
        logging.warning(f"Source '{source_path}' already exists in the database.")
        return True
    logging.info(f"Source '{source_path}' is new.")
    return False

def translate_to_english(text, src_lang='auto'):
    try:
        async def do_translate():
            result = await translator.translate(text, dest='en', src=src_lang)
            return result.text
        return asyncio.run(do_translate())
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return None

def load_pdf(source_path):
    if not source_path.endswith('.pdf'):
        logging.error(f"Error! {source_path} is not a PDF file.")
        return None
    logging.info(f"Loading PDF: {source_path}")
    loader = PyPDFLoader(source_path)
    return loader.load()

def load_youtube(source_url):
    logging.info(f"Loading YouTube video: {source_url}")
    try:
        yt = YouTube(source_url)
        caption = None
        if 'a.en' in yt.captions: caption = yt.captions['a.en']
        elif 'en' in yt.captions: caption = yt.captions['en']
        elif len(yt.captions) > 0:
            caption = list(yt.captions)[0]
            logging.warning(f"No English caption found. Using first available: '{caption.name}'")
        
        if not caption:
            logging.error(f"Error! {source_url} does not have any available captions.")
            return None
            
        processed_caption = clean_srt_captions(caption.generate_srt_captions())
        final_text = processed_caption
        
        if caption.code not in ['en', 'a.en']:
            # It cleans the language code before translation.
            source_language_code = caption.code
            if source_language_code.startswith('a.'):
                source_language_code = source_language_code.split('.')[-1]
                logging.info(f"Cleaned auto-generated lang code from '{caption.code}' to '{source_language_code}' for translator.")

            logging.info(f"Translating content from '{source_language_code}' to English...")
            final_text = translate_to_english(processed_caption, src_lang=source_language_code)

        if not final_text:
            raise Exception("Translation failed or returned empty.")

        doc = Document(
            page_content=final_text,
            metadata={"source": source_url, "title": yt.title, "original_language": caption.code}
        )
        return [doc]

    except Exception as e:
        logging.error(f"Failed to load YouTube URL {source_url}: {e}")
        return None

def load_link(source_url):
    if not source_url.startswith('https://'):
        logging.error(f"Error! {source_url} is not a secure (https) link.")
        return None
    logging.info(f"Loading web page: {source_url}")
    loader = WebBaseLoader(source_url)
    return loader.load()

def split_text(docs):
    if not docs:
        logging.warning("Received an empty or None list of documents to split.")
        return []
    logging.info(f"Splitting {len(docs)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_docs = text_splitter.split_documents(docs)
    logging.info(f"Created {len(split_docs)} chunks.")
    return split_docs

def embed_and_upload(docs):
    if not docs:
        logging.warning("Received no documents to embed and upload. Skipping.")
        return
    logging.info(f"Embedding and uploading {len(docs)} chunks to MongoDB Atlas...")
    collection = client[DB_NAME][COLLECTION_NAME]
    MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=embedding_model,
        collection=collection,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )
    logging.info("Upload complete.")