from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import sqlite3
import mysql_manager as mm
from contextlib import closing
import yelp_data_source
#import google_calendar_data_source
import ranker


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

"""
@app.route('/recme_temp')
def show_yelp_results():
    next_event_datetimeloc = google_calendar_data_source.get_next_event_timedateloc_on_google_calendar()
    return render_template("rec_temp.html", list_results=yelp_data_source.get_results_from_locations(10),
                           next_event = next_event_datetimeloc)
"""

#TODO: recme_temp for now so that link actually works. Comment this out when you're done testing show_yelp_results()
@app.route('/recme_temp')
def recommended():
    return render_template("rec_temp.html", list_results= yelp_data_source.get_results_from_locations(["Italian"]))

@app.route('/restaurant/<restaurant_name>')
def restaurant(restaurant_name):
    return render_template("listview.html", restaurant_name = restaurant_name)

@app.route('/listview.html')
def listview():
    return render_template("listview.html")

@app.route('/profile.html')
def profile():
    # TODO: Need to pass in correct user!, using 'jeet' in the mean time
    cat_names = mm.get_list_categories_for_profile_edit('jeet')
    return render_template("profile.html", category_names=cat_names)


@app.route('/upload', methods=['POST'])
def upload():
    print("Trying to upload categories for user profile")
    selected_categories = request.form.getlist('checkbox')
    # print(selected_categories) #DEBUG
    for cat_name in selected_categories:
        # TODO: Need to pass in correct user!, using 'jeet' in the mean time
        mm.init_category_weight_if_not_present('jeet',cat_name,1.0)
    return redirect("/", code=302)

@app.route('/test_data')
def test_data():
    data=ranker.get_ranking_by_cosine("terry",['Italian']) # need to first update the weights of the user though.
    print(data)
    return render_template("testdata.html")

if __name__ == '__main__':
    app.run()
    # to make public
    # app.run(host='0.0.0.0')
