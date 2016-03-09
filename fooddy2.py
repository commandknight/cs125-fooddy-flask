import sqlite3
import mysql_manager as mm
from contextlib import closing
import yelp_data_source
import google_calendar_data_source
import ranker
import json
from googleapiclient.discovery import build_from_document
from googleapiclient.discovery import build
import httplib2
import random
from oauth2client.client import OAuth2WebServerFlow

from flask import Flask, render_template, session, request, redirect, url_for, abort


# configuration
DATABASE = '/tmp/fooddy.db'
DEBUG = False
SECRET_KEY = 'development_key'
USERNAME = 'admin'
PASSWORD = 'uci'
CLIENT_ID = "113602676382-vom8i9393ldj0vcuk32emk3c4elf20vo.apps.googleusercontent.com"
CLIENT_SECRET = "xdXnSkdHanL361tPp4AZU2HU"


app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template("index.html")

#@app.route('/login.html')
#def show_entries():
#    return render_template("login.html")


@app.route('/login')
def login():
  flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope='https://www.googleapis.com/auth/calendar',
    redirect_uri='http://localhost:5000/oauth2callback',
    approval_prompt='force',
    access_type='offline')

  auth_uri = flow.step1_get_authorize_url()
  return redirect(auth_uri)

@app.route('/signout')
def signout():
  del session['credentials']
  session['message'] = "You have logged out"

  return redirect(url_for('index'))


@app.route('/oauth2callback')
def oauth2callback():
    print("TRYING TO oauth2callback")
    code = request.args.get('code')
    print(code)
    if code:
        print("THE IF STATEMENT IS OK")
        # exchange the authorization code for user credentials
        flow = OAuth2WebServerFlow(CLIENT_ID,
                                   CLIENT_SECRET,
                                   "https://www.googleapis.com/auth/calendar")
        flow.redirect_uri = request.base_url
        # flow.redirect_uri = 'http://localhost:5000'
        print("TEST", flow.redirect_uri)
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            print("Unable to get an access token because ", e.message())
        # store these credentials for the current user in the session
        # This stores them in a cookie, which is insecure. Update this
        # with something better if you deploy to production land
        print("TEST2", type(credentials))
        #session['credentials'] = credentials
    return 'I HATE LIFE'


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


@app.route('/calendartest')
def calendartest():
    credentials = request.session['credentials']
    next_event = google_calendar_data_source.get_next_event_timedateloc_on_google_calendar(credentials)
    return render_template("calendartest.html", event = next_event)

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
    app.run(host='localhost')
    # to make public
    # app.run(host='0.0.0.0')
