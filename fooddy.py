from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import sqlite3
from contextlib import closing


# configuration
DATABASE = '/tmp/fooddy.db'
DEBUG = False
SECRET_KEY = 'development_key'
USERNAME = 'admin'
PASSWORD = 'uci'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login.html')
def show_entries():
    return render_template("login.html")

@app.route('/listview.html')
def listview():
    return render_template("listview.html")

@app.route('/profile.html')
def profile():
    import mysql_manager as mm
    cat_names = mm.get_list_of_category_names()
    mm.close_connection()
    return render_template("profile.html", category_names=cat_names)

# TODO: DO WE NEED THIS?? If not, please delete. [CA]
# def connect_db():
#     return sqlite3.connect(app.config['DATABASE'])
#
# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()
#
# @app.before_request
# def before_request():
#     g.db = connect_db()
#
# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, 'db', None)
#     if db is not None:
#         db.close()
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('show_entries'))
#     return render_template('login.html', error=error)
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
