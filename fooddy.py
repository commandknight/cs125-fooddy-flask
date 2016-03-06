from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import sqlite3
import mysql_manager as mm
from contextlib import closing
import yelp_data_source
import google_calendar_data_source


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

@app.route('/recme_temp')
def show_yelp_results():
    next_event_datetimeloc = google_calendar_data_source.get_next_event_timedateloc_on_google_calendar()
    return render_template("rec_temp.html", list_results=yelp_data_source.get_results_from_location(10),
                           next_event = next_event_datetimeloc)

@app.route('/restaurant/<restaurant_name>')
def restaurant(restaurant_name):
    return render_template("listview.html", restaurant_name = restaurant_name)

@app.route('/listview.html')
def listview():
    return render_template("listview.html")

@app.route('/profile.html')
def profile():
    cat_names = mm.get_list_of_category_names()
    return render_template("profile.html", category_names=cat_names)


if __name__ == '__main__':
    app.run()
