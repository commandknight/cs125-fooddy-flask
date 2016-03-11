import datetime
import json

import httplib2
from flask import Flask, render_template, request, redirect, url_for, session
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager, UserMixin
from googleapiclient import discovery
from oauth2client import client
from oauth2client.client import OAuth2WebServerFlow

import google_calendar_data_source
import mysql_manager as mm
import yelp_data_source
from models.UserModel import User

# app configuration
DEBUG = False
SECRET_KEY = 'development_key'
USERNAME = 'admin'
PASSWORD = 'uci'
CLIENT_ID = "113602676382-vom8i9393ldj0vcuk32emk3c4elf20vo.apps.googleusercontent.com"
CLIENT_SECRET = "xdXnSkdHanL361tPp4AZU2HU"

# App Init
app = Flask(__name__)
app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


# Helper Functions
@login_manager.user_loader
def user_loader(user_name):
    temp_user = mm.get_user(user_name)
    if temp_user is not None:
        return User(temp_user)
    return None


# HOME PAGE
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        form_password = request.form['user_password']
        user = mm.get_user(user_name)
        if user:
            muser = User(user)
            if muser.password == form_password:
                # if valid login info:
                # print(muser) #DEBUG
                login_user(muser) # Save user in context as "logged_in"
                return render_template("index.html")
                #redirect(request.args.get('next') or url_for('index')) #allows login page to act as inbetween
            else:
                print("ERROR in logging in")
                return render_template("login.html", error_msg="You entered a wrong password, please try again")
        else:
            return render_template("login.html", error_msg="Unknown username, please try again")
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return render_template("logout.html")


@app.route('/auth_google')
def auth_google():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        global http_auth
        http_auth = credentials.authorize(httplib2.Http())
        #service = discovery.build('calendar', 'v3', http=http_auth)
        return redirect(url_for('index'))


@app.route('/get_location')
def get_location(http_auth):
    service = discovery.build('calendar', 'v3', http=http_auth)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    # note: events_result['items'][0] is a Event resource object
    # see: https://developers.google.com/google-apps/calendar/v3/reference/events
    if 'location' in events_result['items'][0].keys():
        location = events_result['items'][0]['location']
    else:
        location = 'unspecified'
    return location


@app.route('/oauth2callback')
def oauth2callback():
    print('HERE')
    flow = client.flow_from_clientsecrets(
        'resources/google_calendar_client_secret.json',
        scope='https://www.googleapis.com/auth/calendar.readonly',
        redirect_uri=url_for('oauth2callback', _external=True))
    print('flow was established')
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        return redirect(url_for('index'))


@app.route('/recommended')
def recommended():
    # Right now, we are using a static category_filter=["Italian"],
    # TODO: later use the user's checked categories.
    user_categories = mm.get_list_of_category_names_user_likes("jeet")
    # location = get_location(http_auth)
    # print(location)
    return render_template("recommended.html",
                           list_results= yelp_data_source.get_results_from_locations(user_categories))

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

@app.route('/profile/<username>')
@login_required
def profile(username):
    print(current_user.get_id()) #EXAMPLE TO GET USER
    username= "jeet" # TODO: Need to pass in correct user!, using 'jeet' in the mean time
    cat_names = mm.get_list_categories_for_profile_edit(username)
    return render_template("profile.html", category_names=cat_names)


@app.route('/upload', methods=['POST','GET'])
@login_required
def upload():
    username = "jeet"
    if request.method == 'GET':
        return redirect("/", code=302)
    # print("Trying to upload categories for user profile")
    selected_categories = request.form.getlist('checkbox')
    # print(selected_categories) #DEBUG
    for cat_name in selected_categories:
        # TODO: Need to pass in correct user!, using 'jeet' in the mean time
        mm.init_category_weight_if_not_present(username,cat_name,1.0)
    return render_template("index.html", logged_in=True, username = username, code=302)


if __name__ == '__main__':
    app.run(host='localhost')
    # to make public
    # app.run(host='0.0.0.0')
