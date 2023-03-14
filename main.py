import os
from flask import Flask, render_template, request, redirect, url_for

server = Flask(__name__)

@server.route('/')
def index():
    return render_template('index.html')

@server.route('/about')
def about():
    return render_template('about.html')

@server.route('/add')
def add():
    return render_template('add.html')

@server.route('/post')
def post():
    return render_template('post.html')

if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))