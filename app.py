# app.py

from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'analise_filmes.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
