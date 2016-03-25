import json
import math
import time
import urllib

import numpy as np
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import mysql_manager as mm

consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'
google_places_key = "AIzaSyBrElDm-bOxHup93M1QLfWXYjpYYoReGjg"
auth = Oauth1Authenticator(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    token=token,
    token_secret=token_secret
)
yelp_client = Client(auth)


# Constants
radiusToSearch = 40000/5 # in meters 40000 is 25 miles
limit = 20  # number of results per yelp query

class YelpData:
    def __init__(self, business):
        self.restaurant_info = business  # dictionary information for the restaurant/business
        self.restaurant_vector = self.__get_restaurant_vector()  # restaurant weights
        self.cosine_sim = -1  # cosine simlarity.


    # return weight vectors for restaurant
    def __get_restaurant_vector(self):
        self.list_categories = []
        vec = np.zeros(mm.num_categories)
        for category_list_item in self.restaurant_info.categories:
            category = category_list_item.name
            if category in mm.set_categories:  # add only the categories that we have.
                vec[mm.category_dict[category]] = 1
                self.list_categories.append(category)
        return vec

    def __str__(self):
        return self.restaurant_info['business_id']


# Query the Yelp API for a Business, by passing restaurant_id.
def get_business_by_id(restaurant_id):
    response = yelp_client.get_business(restaurant_id)
    return response.business  # returns a Yelp BUSINESS Object


def get_location_from_coordinates(long, lat) -> str:
    LOCATION = str(long) + "," + str(lat)
    RADIUS = 1
    MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
             '?location=%s'
             '&radius=%s'
             '&key=%s') % (LOCATION, RADIUS, google_places_key)
    # grabbing the JSON result
    response = urllib.request.urlopen(MyUrl)
    jsonRaw = response.read().decode("utf-8")
    jsonData = json.loads(jsonRaw)
    # parse for location name i.e. San Francisco
    location_name = jsonData['results'][0]['vicinity']
    return location_name


def get_rotation_matrix(recentered_outer_vector):
    if (recentered_outer_vector[1] == 0 or recentered_outer_vector[0] == 0):
        if (recentered_outer_vector[1] == 0):  # if y is zero we want to rotate x to y so we have a length.
            theta = np.deg2rad(90)
        elif (recentered_outer_vector[0] == 0):  # if x is zero, no rotations needed.
            theta = np.deg2rad(0)
    else:
        theta = np.arctan(recentered_outer_vector[0] / recentered_outer_vector[1])
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))
    return R



    # get leftmost point, center both points by the left most point. find slope to determine how to find angle. find angle,
    # rotate it, find box, rotate it back, translate it back.

# expects it in long,lat format. (x,y)
def get_bounding_box(coords):
    # width is Golden Ratio. L/1.62
    ratio = 1.62
    long1 = coords[0][0]
    long2 = coords[1][0]
    left_most_point_index = np.array([long1, long2]).argmin()
    right_most_point_index = left_most_point_index ^ 1  # XOR
    translate_x = coords[left_most_point_index][0]
    translate_y = coords[left_most_point_index][1]
    recentered_outer_vector = np.array(
        [coords[right_most_point_index][0] - translate_x, coords[right_most_point_index][1] - translate_y])
    R = get_rotation_matrix(recentered_outer_vector)
    rotated_point = np.array(np.dot(R, recentered_outer_vector.transpose()))[0]
    lower_left = np.array([-rotated_point[1] / ratio / 2, 0])
    lower_right = np.array([rotated_point[1] / ratio / 2, 0])
    upper_left = np.array([-rotated_point[1] / ratio / 2, rotated_point[1]])
    upper_right = np.array([rotated_point[1] / ratio / 2, rotated_point[1]])
    boundary_points = np.array([lower_left, lower_right, upper_left, upper_right]).transpose()
    boundary_points = np.dot(np.linalg.inv(R), boundary_points)  # rotate back to original angle.
    translate_matrix = np.dot(np.array([[translate_x, 0], [0, translate_y]]), np.ones([2, 4]))
    boundary_points = boundary_points + translate_matrix
    return boundary_points


def get_southwest_northeast_coords(coords):
    lat1 = coords[0][1]
    lat2 = coords[1][1]
    long1 = coords[0][0]
    long2 = coords[1][0]
    left_most_point_index = np.array([long1, long2]).argmin()
    top_most_point_index = np.array([lat1, lat2]).argmax()
    southwest_point = (coords[left_most_point_index][0], coords[top_most_point_index ^ 1][1])
    northeast_point = (coords[left_most_point_index ^ 1][0], coords[top_most_point_index][1])
    return southwest_point, northeast_point  # returns in x,y (longitude, latitude fashion)


# pass in a list of tuples for locations. Default
# category_filter is a list of category namesis SF and San Jose
# coords = lat,long (y,x) --> swap to x,y so it is more familiar and less confusing
def swap_coords(coords):
    a = []
    for tup in coords:
        a.append((tup[1], tup[0]))
    return a

def parse_yelp_responses(yelp_api_response):
    responses =[]
    for business in yelp_api_response.businesses:
        for category in business.categories:  # if it has a category in our categories, we add it.
            if category.alias in mm.set_aliases:
                responses.append(business)
                break
    return responses

def filter_results_by_rectangle(coords, list_businesses):
    boundary_points = get_bounding_box(coords);
    for business in list_businesses:
        business.location.coordinate.latitude
        business.location.coordinate.longitude
    return None

# coords are in lat/long
def get_results_from_locations(num_results, coords, radius):
    # parse location if two locations given
    normal_coords = swap_coords(coords)
    iterations = math.ceil(num_results / limit)
    responses = []

    params = {
        'category_filter': "food",
        'limit': limit,
    }
    if len(normal_coords) == 2:
        # find bounding box
        southwest_point, northeast_point = get_southwest_northeast_coords(normal_coords);
        for i in range(iterations):
            params['offset'] = i * limit
            yelp_api_response = yelp_client.search_by_bounding_box(southwest_point[1], southwest_point[0], northeast_point[1],
                                                          northeast_point[0], **params)
            responses += parse_yelp_responses(yelp_api_response)

        return responses

    elif len(normal_coords) == 1:
        long = normal_coords[0][0]
        lat = normal_coords[0][1]
        for i in range(iterations):
            params['radius_filter'] = radius
            params['offset'] = i * limit
            yelp_api_response = yelp_client.search_by_coordinates(lat, long, **params)

            responses += parse_yelp_responses(yelp_api_response)

        return responses

    else:
        raise Exception("Please provide no more than two location coordinate sets")


# pass in location as an address String
def get_results_from_address(location, num_results, radius=radiusToSearch):
    iterations = math.ceil(num_results / limit)
    responses = []
    params = {
        'category_filter': "food",
        'limit': limit,
        'radius_filter': radius
    }

    for i in range(iterations):
        params['offset'] = i * limit
        yelp_api_response = yelp_client.search(location, **params)
        responses += parse_yelp_responses(yelp_api_response)

        return responses


def get_yelp_data(list_businesses):
    """
    Given a list of Yelp Businesses from Yelp API, returns a list of YelpData Objects
    :param list_businesses: list of businesses from Yelp API
    :return: List(YelpData)
    """
    return [YelpData(bus) for bus in list_businesses]




def get_restaurant_vectors_by_query(coords, num_results, radius=radiusToSearch):
    list_businesses = get_results_from_locations(num_results, coords=coords, radius=radius)
    return get_yelp_data(list_businesses)

def get_restaurant_vectors_by_address(location, num_results):
    list_businesses = get_results_from_address(location, num_results)
    return get_yelp_data(list_businesses)