import os, sys
sys.path.insert(0, "c:/users/tranc2/appdata/local/programs/python/python312/lib/site-packages")
import optparse
from flask import Flask, render_template, request, Response # type: ignore
from semantic_search import main, create_embedding
import time

app = Flask(__name__)

# Initialize

# all_messages=[{"role": "system", "content": main.gpt_instructions}]
all_messages=[{"role": "system", "content": "You're a bot"}]

@app.route('/')
def home():
    return render_template("home_page.html", title="Database Companion Home Page")

@app.route('/articles', strict_slashes=False, methods=['POST'])
def article():
    global all_messages
    user_input = request.form["user input"]
    # Get user data.
    all_messages, message = main.chat(all_messages, user_input)
    top_10 = create_embedding.query(message)
    return render_template("articles_page.html", title="Related Articles", top_10 = top_10)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8100)