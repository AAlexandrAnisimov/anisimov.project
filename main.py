import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from config import Config

server = Flask(__name__)
server.config.from_object(Config)

@server.before_request
def before_request():
    g.user_id = None
    g.user_nickname = None
    g.user_role = None

    if ('user_id' in session) and ('user_role' in session) and ('user_nickname' in session):
        g.user_id = session['user_id']
        g.user_nickname = session['user_nickname']
        g.user_role = session['user_role']

@server.route('/')
def index():
    return render_template('index.html')

@server.route('/about')
def about():
    return render_template('about.html')

@server.route('/add')
def add():
    return render_template('add.html')

@server.route('/addcourse', methods=['POST'])
def addcourse():
    title = request.form['title']
    subtitle = request.form['subtitle']
    content = request.form['content']

    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.callproc('create_course', (g.user_id, title, subtitle, content))
    connection.close()

    return redirect(url_for("index"))

@server.route('/post')
def post():
    return render_template('post.html')

@server.route('/users/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('users/sign_in.html')
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('user_nickname', None)
        session.pop('user_role', None)

        connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
        connection.autocommit = True

        login = request.form['login']
        password = request.form['password']

        cursor = connection.cursor()
        cursor.callproc('login_user', (login, password))

        exit_code = cursor.fetchall()[0][0]
        if exit_code != -1:
            session['user_id'] = exit_code
            session['user_nickname'] = login

            cursor.execute(f"SELECT get_user_info({session['user_id']})")
            result = cursor.fetchall()[0]
            (u_id, u_login, u_password, u_email, u_role) = result[0][1:-1].split(',')

            session['user_role'] = u_role
            connection.close()

            return redirect(url_for("index"))
        else:
            connection.close()
            flash('There is no user with that login')
            return render_template('users/sign_in.html')

if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))