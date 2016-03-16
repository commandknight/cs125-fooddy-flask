import datetime

import httplib2
from flask import Flask, render_template, request, redirect, url_for, session
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from googleapiclient import discovery
from oauth2client import client

import mysql_manager as mm
import yelp_data_source
import ranker
from models.UserModel import User
import time;
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


def is_google_auth():
    """
    Function that returns true if the user has autheticated Google Calender Read Only Access
    :return: Boolean
    """
    if 'credentials' not in session.keys():
        return False
    # print(session['credentials'])  # DEBUG
    return True


# HOME PAGE
@app.route('/')
def index():
    return render_template("index.html")

# todo: on login, degenerate the user weights
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        form_password = request.form['user_password']
        if request.form['submit'] == 'Sign In':
            user = mm.get_user(user_name)
            if user:
                muser = User(user)
                if muser.password == form_password:
                    login_user(muser)  # Save user in context as "logged_in"
                    return redirect(url_for('index'))
                    # redirect(request.args.get('next') or url_for('index')) #allows login page to act as inbetween
                else:
                    # print("ERROR in logging in") #DEBUG
                    return render_template("login.html", error_msg="You entered a wrong password, please try again")
            else:
                return render_template("login.html", error_msg="Unknown username, please try again")
        elif request.form['submit'] == 'Sign Up':
            # print("Trying to sign user up") #DEBUG
            if user_name is "" or form_password is "":
                return render_template("login.html", error_msg="Empty Username or Password Fields, please try again")
            mm.insert_new_user_profile(user_name, form_password)
            new_user = User((user_name, form_password))
            mm.init_category_weight_vector_for_user(user_name, .015)
            login_user(new_user)
            return redirect(url_for('index'))
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    session.clear()
    return render_template("logout.html")


@app.route('/auth_google')
def auth_google():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    return redirect(url_for('index'))


@app.route('/get_location')
def get_location(http_auth):
    service = discovery.build('calendar', 'v3', http=http_auth)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    # note: events_result['items'][0] is a Event resource object
    # see: https://developers.google.com/google-apps/calendar/v3/reference/events
    index_of_valid_event = 0
    # need to handle when user has no more events in events_result
    for i in range(len(events_result['items'])):
        example = events_result['items'][i]['start']
        if 'dateTime' in example.keys():
            index_of_valid_event = i
            # print(index_of_valid_event) #DEBUG
            break
    if 'location' in events_result['items'][index_of_valid_event].keys():
        location = events_result['items'][index_of_valid_event]['location']
    else:
        location = 'unspecified'
    return location


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'resources/google_calendar_client_secret.json',
        scope='https://www.googleapis.com/auth/calendar.readonly',
        redirect_uri=url_for('oauth2callback', _external=True))
    # print('flow was established') # DEBUG
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        global http_auth
        http_auth = credentials.authorize(httplib2.Http())
        # print(http_auth)
        return redirect(url_for('index'))


@app.route('/recommended', methods=["GET", "POST"])
def recommended():
    username = current_user.get_id()
    user_categories = mm.get_list_of_category_names_user_likes(username)
    if request.method=="POST":

        for i in request.form.items():
            print(i)
        if request.form['confirm_current_loc'] == "OK":
            long = request.form.get("current_location_longitude")
            lat = request.form.get("current_location_latitude")

            print(long, lat)

            if is_google_auth():
                location = get_location(http_auth)

            elif not is_google_auth():
                location = "Connect with Google Calendar to see your next event's location!"

            # TODO: PASS IN LONGITUDE AND LATITUDE IN YELP RETURN STATEMENT BELOW.................
            # TODO: PASS IN LONGITUDE AND LATITUDE IN YELP RETURN STATEMENT BELOW.................
            # TODO: PASS IN LONGITUDE AND LATITUDE IN YELP RETURN STATEMENT BELOW.................
            # TODO: PASS IN LONGITUDE AND LATITUDE IN YELP RETURN STATEMENT BELOW.................
            print(lat,long)
            return render_template("recommended.html",
                                   list_results=ranker.get_ranking_by_probabilistic_cosine(current_user.get_id(), user_categories, coords=[(lat,long)]),
                                   next_location =location)
    else:
        print('still using GET')
        if is_google_auth():
            location = get_location(http_auth)
        elif not is_google_auth():
            location = "Connect with Google Calendar to see your next event's location!"


        return render_template("recommended.html",
                               list_results=ranker.get_ranking_by_probabilistic_cosine(current_user.get_id(), user_categories),
                               next_location=location)

#Single Restaurant View
@app.route('/restaurant/<restaurant_id>')
def restaurant(restaurant_id):
    business = yelp_data_source.get_business_by_id(restaurant_id)  # this is a dictionary
    username = current_user.get_id();
    categories = ['Indian', 'Italian']
    mm.update_category_weights_by_visit(username, categories);
    print(mm.get_user_weights_vector(username))
    return render_template("restaurant.html", business=business)


@app.route('/profile/<username>')
@login_required
def profile(username):
    # print(current_user.get_id())  # EXAMPLE TO GET USER
    username = current_user.get_id()
    cat_names = mm.get_list_categories_for_profile_edit(username)
    return render_template("profile.html", category_names=cat_names)


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    username = current_user.get_id()
    if request.method == 'GET':
        return redirect("/", code=302)
    # print("Trying to upload categories for user profile")
    selected_categories = request.form.getlist('checkbox')
    # print(selected_categories) #DEBUG
    for cat_name in selected_categories:
        mm.init_category_weight_if_not_present(username, cat_name, 1.0)
    return render_template("index.html", logged_in=True, username=username, code=302)

# todo: rating upload and do stuff with it.
@app.route('/rating', methods=['POST'])
@login_required
def update_user_weights():
    username = current_user.get_id()
    rating = request.form['rating']
    business_id = request.form['business_id']
    categories = request.form['categories']
if __name__ == '__main__':
    app.run(host='localhost')
    # to make public
    # app.run(host='0.0.0.0')
