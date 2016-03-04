from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import sqlite3
from contextlib import closing

app = Flask(__name__)
app.config.update(dict(
    DATABASE = 'fooddy.db',
    DEBUG=False,
    SECRET_KEY='dev_key',
    USERNAME='admin',
    PASSWORD='uci'
))
app.config.from_envvar('FOODDY_SETTINGS', silent=True)


@app.route('/')
def main_page():
    import mysql_manager
    test_list = mysql_manager.get_test_data()
    mysql_manager.close_connection()
    return 'JEET ' + ' NAGDA' + str(test_list[0])


if __name__ == '__main__':
    app.run()

