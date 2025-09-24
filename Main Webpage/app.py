import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import logging

# --- IMPORT HELPER FUNCTION ---
from loading_doc_helper import (
    load_pdf, load_youtube, load_link, 
    split_text, embed_and_upload,
    check_if_source_exists
)

# --- FLASK APP SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- FLASK WEB ROUTES ---

@app.route('/', methods=['GET'])
def home():
    """Renders the main page with only the ingestion form."""
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest():
    """Handles the document ingestion pipeline, including a duplicate check."""
    source_path = None
    source_name = None

    if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
        file = request.files['pdf_file']
        source_path = secure_filename(file.filename)
        source_name = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
    elif 'source_url' in request.form and request.form['source_url'].strip():
        source_path = request.form['source_url'].strip()
        source_name = source_path
    if not source_path:
        flash("No valid input provided. Please upload a PDF or enter a URL.", "warning")
        return redirect(url_for('home'))

    logging.warning(f"CHECKING:-----{source_name}")
    if check_if_source_exists(source_name):
        
        flash(f"KNOWLEDGE ALREADY EXISTS: '{source_name}' has already been ingested.", "warning")
        return redirect(url_for('home'))

    source_data = None
    try:
        if source_path.endswith('.pdf'):
            file = request.files['pdf_file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], source_path)
            file.save(filepath)
            source_data = load_pdf(filepath)
            os.remove(filepath)
        elif 'youtube.com' in source_path or 'youtu.be' in source_path:
            source_data = load_youtube(source_path)
        else:
            source_data = load_link(source_path)
        
        # The main ingestion pipeline
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
    app.run(debug=True)

