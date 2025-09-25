# PeTS (Personal Translator)

A web application built with Flask for translating text between Finnish and English. This project uses a powerful, locally-run, open-source language model to provide fast and accurate translations.

## Current Status (As of September 2025)

The project is currently in the final development phase.

* **Web Interface:** The user interface is complete, allowing users to input text.
* **Translation Engine:** The translation functionality is currently disabled in the UI while the backend is being integrated.
* **Model Evaluation:** We have successfully evaluated the `Helsinki-NLP/opus-mt` models for both `en-fi` and `fi-en` translation. Extensive testing shows the model provides high-quality, grammatically correct translations that are highly competitive with commercial services like Google Translate. The model is confirmed and ready for integration.

## Core Technology

* **Backend:** Python 3, Flask
* **Frontend:** HTML, [Tailwind CSS](https://tailwindcss.com/)
* **Translation Model:** [Helsinki-NLP/opus-mt](https://huggingface.co/Helsinki-NLP) series via the Hugging Face `transformers` library.

## Key Resources & Datasets

This project's development and evaluation relied on the following key resources:

* **Primary Model:** [Helsinki-NLP/opus-mt-fi-en](https://huggingface.co/Helsinki-NLP/opus-mt-fi-en) - The pre-trained, open-source model from Hugging Face that serves as the core translation engine.
* **Benchmarking Tool:** [googletrans 4.0.0-rc1](https://pypi.org/project/googletrans/4.0.0-rc1/) - A Python library used to compare the local model's performance against Google Translate's public API.
* **Data Exploration:** [ParaCrawl (Finnish-English)](https://paracrawl.eu/) - A large parallel corpus that was analyzed and prepared during the initial data exploration phase of the project.

## How to Run the Web Application

To run the web interface locally, follow these steps.

### Prerequisites

* Python 3.6+

### Setup

1.  **Clone or download the project files** into a new directory.

2.  **Create and activate a virtual environment** (recommended):
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # For Windows
    py -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the necessary Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    flask run
    ```

5.  **View the application:** Open your web browser and navigate to `http://127.0.0.1:5000`.

Make sure to set up your connection string in **MONGO_URI**
Make sure to set up your OpenAI API Key