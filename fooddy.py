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

@app.route('/recommended')
def recommended():
    # Right now, we are using a static category_filter=["Italian"],
    # TODO: later use the user's checked categories.
    user_categories = mm.get_list_of_category_names_user_likes("jeet")
    return render_template("recommended.html", list_results= yelp_data_source.get_results_from_locations(user_categories))


# This is used AFTER we display recme_temp (list of restaurants)
@app.route('/restaurant/<restaurant_id>')
def restaurant(restaurant_id):
    business = yelp_data_source.get_business_by_id(restaurant_id) #this is a dictionary
    return render_template("restaurant.html", business= business)


@app.route('/profile.html')
def profile():
    # TODO: Need to pass in correct user!, using 'jeet' in the mean time
    cat_names = mm.get_list_categories_for_profile_edit('jeet')
    return render_template("profile.html", category_names=cat_names)


@app.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'GET':
        return redirect("/", code=302)
    print("Trying to upload categories for user profile")
    selected_categories = request.form.getlist('checkbox')
    # print(selected_categories) #DEBUG
    for cat_name in selected_categories:
        # TODO: Need to pass in correct user!, using 'jeet' in the mean time
        mm.init_category_weight_if_not_present('jeet',cat_name,1.0)
    return redirect("/", code=302)


if __name__ == '__main__':
    # IMPORT HERE
    app.run()
    # to make public
    # app.run(host='0.0.0.0')
