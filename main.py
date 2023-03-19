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
    if g.user_nickname == None:
        return redirect(url_for("login"))
    else:
        connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
        connection.autocommit = True
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM courses")
        result = cursor.fetchall()
        connection.close()
        
        courses = []
        for course_id, user_id, title, subtitle, day_posted, content in result:
            course = {
                "id": course_id,
                "title": title,
                "subtitle": subtitle,
                "day_posted": day_posted
            }
            courses.append(course)

        return render_template('index.html', c_courses = courses)

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


@server.route('/course/<course_id>', methods=['GET'])
def course(course_id):

    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM courses WHERE courses.course_id = %(c_id)s AND courses.fk_user_id = %(u_id)s""",
                   {'c_id': course_id, 'u_id': g.user_id})
    result = cursor.fetchall()
    connection.close()

    courses = []
    for cid, uid, title, subtitle, day_posted, content in result:
        course = {
            "title": title,
            "subtitle": subtitle,
            "day_posted": day_posted,
            "content": content
        }
        courses.append(course)

    return render_template('course.html', c_courses = courses)

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
        
@server.route('/admin')
def admin():
    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users_lst = cursor.fetchall()
    connection.close()

    return render_template('admin.html', users = users_lst)

@server.route('/adduser', methods=['POST'])
def adduser():
    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    login = request.form['login']
    password = request.form['password']
    email = request.form['email']
    fname = request.form['fname']
    lname = request.form['lname']
    
    role = request.form['role']
    curator = request.form['curator']
    group = request.form['group']

    if (login == '' or
        password == '' or
        email == '' or 
        fname == '' or 
        lname == ''):
        flash('Заповніть усі поля, позначені *!')
    elif len(login) < 6:
        flash('Логін занадто короткий (потрібно мінімум 6 символів)!')
    elif len(password) < 6:
        flash('Пароль занадто короткий (потрібно мінімум 6 символів)!')
    else:
        cursor = connection.cursor()
        
        cursor.execute("""SELECT * FROM users WHERE users.user_login = %(u_login)s""", {'u_login': login})
        result = cursor.fetchall()

        users = []
        for uid, log, pas, em, fn, ln, r in result:
            users.append(uid)

        if users != []:
            flash('Користувача з таким логіном вже зареєстровано')
        else:
            cursor.execute("INSERT INTO users (user_login, user_password, user_email, user_fname, user_lname, user_role ) VALUES (%s, %s, %s, %s, %s, %s)", 
                          (login, password, email, fname, lname, role))
            flash('Користувача успішно додано')

    connection.close()
    return redirect(url_for('admin')) 

@server.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):
    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = {0}'.format(id))
    flash('Користувача успішно видалено')
    return redirect(url_for('admin'))

@server.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = (%s)', (id))
    result = cursor.fetchall()
    connection.close()

    users_lst = []
    for uid, login, password, email, fn, ln, role in result:
        user = {
            "id": uid,
            "login": login,
            "password": password,
            "email": email,
            "fname": fn,
            "lname": ln
        }
        users_lst.append(user)

    return render_template('edit.html', users = users_lst)

@server.route('/update/<id>', methods=['POST'])
def update(id):
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']

    connection = psycopg2.connect(server.config['SQLALCHEMY_DATABASE_URI'])
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute("""UPDATE users SET user_fname = %s, user_lname = %s, user_email = %s WHERE user_id = %s""",
                   (fname, lname, email, id))
    connection.close()

    return redirect(url_for('admin'))

if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))