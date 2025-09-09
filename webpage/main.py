from flask import Flask, render_template

# Initialize the Flask application
app = Flask(__name__)

# Define the route for the homepage
@app.route('/')
def homepage():
    """
    Renders the main homepage of the PeTS application.
    """
    # The render_template function looks for the file in a 'templates' folder
    return render_template('index.html')

# This block allows you to run the app directly from the command line
if __name__ == '__main__':
    # debug=True will automatically reload the server when you make changes
    app.run(debug=True)

