import os
from config import *
from flask import Flask, request, redirect, url_for, render_template

server = Flask(__name__)

@server.route('/')
def home():
    return render_template('ind.html')

if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
