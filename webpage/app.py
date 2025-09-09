from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def homepage():
    if request.method == 'POST':
        text_to_translate = request.form.get('text_to_translate')
        ## Update later

        return render_template('index.html')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)