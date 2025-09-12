from flask import Flask, render_template, request
from transformers import MarianMTModel, MarianTokenizer
from googletrans import Translator

translator = Translator()
model_name = 'Helsinki-NLP/opus-mt-fi-en'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def gg_translate(text):
    try:
        result = translator.translate(text, src='fi', dest ='en')
        if result and result.text:
            translation = result.text
            return f"From Google: {translation}"
        else:
            return f"Invalid Translation for: {text}"
    
    except Exception as e:
        print(f"Error Translating: {e}")
        return f"Translation Failed: {text}"

def model_translate(text):
    batch = tokenizer(text, return_tensors= 'pt', padding = True)
    gen  = model.generate(**batch)
    return tokenizer.batch_decode(gen, skip_special_tokens = True)[0]



app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def homepage():
    translated_text = None
    original_text = None
    model_choice  = 'helsinki'
    if request.method == 'POST':
        text_to_translate = request.form.get('text_to_translate')
        original_text = request.form['input_text']
        model_choice = request.form['model_choice']
        if model_choice == 'helsinki':
            translated_text = model_translate(original_text)
        elif model_choice == 'google':
            translated_text = gg_translate(original_text)
        return render_template('index.html', translated_text = translated_text, original_text = original_text, model_choice = model_choice)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)