from yelpapi import YelpAPI
import pprint as pp
import math;
import time;
import urllib;
import json;
import mysql_manager as mm
import numpy as np;
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

class YelpData:

    def __init__(self, business):
        self.restaurant_info = business;  # dictionary information for the restaurant/business
        self.restaurant_vector = self.__get_restaurant_vector(); # restaurant weights
        self.cosine_sim = -1; # cosine simlarity.


    # TODO: remove conditional after category table is fixed
    # return weight vectors for restaurant
    def __get_restaurant_vector(self):
        vec = np.zeros(num_categories);
        for category_list_item in self.restaurant_info['categories']:
            category = category_list_item[0]
            print(category)
            if(category in category_dict.keys()):
                vec[category_dict[category]] = 1;
        return vec;



consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'

google_places_key = "AIzaSyBrElDm-bOxHup93M1QLfWXYjpYYoReGjg"

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)

auth = Oauth1Authenticator(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    token=token,
    token_secret=token_secret
)

yelp_client = Client(auth)

category_dict = mm.get_category_dict();
num_categories = len(category_dict)
category_name_to_alias_dict = mm.get_category_name_to_alias_dict();


# Query the Yelp API for a Business, by passing restaurant_id.
def get_business_by_id(restaurant_id):
    response = yelp_api.business_query(id=restaurant_id)
    return response  # returns a Yelp BUSINESS dictionary with keys: name, id, location, etc.

def get_location_from_coordinates(long, lat) -> str:
    LOCATION = str(long) + "," + str(lat)
    RADIUS = 1;
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

    # get leftmost point, center both points by the left most point. find slope to determine how to find angle. find angle,
    # rotate it, find box, rotate it back, translate it back.


def get_rotation_matrix(recentered_outer_vector):
    if(recentered_outer_vector[1]==0 or recentered_outer_vector[0] == 0):
        if(recentered_outer_vector[1]==0): # if y is zero we want to rotate x to y so we have a length.
            theta = np.deg2rad(90)
        elif(recentered_outer_vector[0]==0):# if x is zero, no rotations needed.
            theta = np.deg2rad(0);
    else:
        theta = np.arctan(recentered_outer_vector[0]/recentered_outer_vector[1])
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))
    return R;

def get_bounding_box(coords):

    # width is Golden Ratio. L/1.62
    long1 = coords[0][0]
    long2 = coords[1][0]
    left_most_point_index = np.array([long1,long2]).argmax()
    right_most_point_index = left_most_point_index ^ 1 # XOR
    translate_x = coords[left_most_point_index][0];
    translate_y = coords[left_most_point_index][1];
    recentered_outer_vector = np.array([coords[right_most_point_index][0]-translate_x, coords[right_most_point_index][1]-translate_y]);
    R = get_rotation_matrix(recentered_outer_vector);
    rotated_point = np.array(np.dot(R, recentered_outer_vector.transpose()))[0]
    lower_left = np.array([-rotated_point[1]/1.62/2, 0])
    lower_right = np.array([rotated_point[1]/1.62/2, 0])
    upper_left = np.array([-rotated_point[1]/1.62/2, rotated_point[1]])
    upper_right = np.array([rotated_point[1]/1.62/2, rotated_point[1]])
    boundary_points = np.array([lower_left, lower_right, upper_left, upper_right]).transpose();
    boundary_points = np.dot(np.linalg.inv(R), boundary_points); # rotate back to original angle.
    translate_matrix = np.dot(np.array([[translate_x,0],[0,translate_y]]), np.ones([2,4]))
    boundary_points = boundary_points + translate_matrix;
    return boundary_points


# pass in a list of tuples for locations. Default
# category_filter is a list of category namesis SF and San Jose
def get_results_from_locations(category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)], num_of_results=40, limit = 20):
    # parse location if two locations given

    aliases = ''
    for category in category_filter:
        aliases += category_name_to_alias_dict[category] + ','
    aliases = aliases[:-1]  # strip the last comma

    if len(coords) == 2:
        params = {
            'category_filter': aliases,
            'limit': limit,
        };
        # find bounding box

        yelp_client.search_by_bounding_box(37.900000, -122.500000,37.788022,-122.399797, **params)

    elif len(coords) == 1:
        loc1 = coords[0];
        long = loc1[0];
        lat = loc1[1];
        loc_coords = str(long) + "," + str(lat);
        location = get_location_from_coordinates(long, lat);
        print (loc_coords, location)

    else:
        raise Exception("Please provide no more than two location coordinate sets");
    iterations = math.ceil(num_of_results / limit);

    params = {
        'category_filter': aliases,
        'limit': limit,
    };

    client.search_by_coordinates(37.788022, -122.399797, **params)

    responses = [];

    for i in range(iterations):
        time.sleep(.3)
        response = yelp_api.search_query(category_filter=aliases, location=location, offset=limit*i, cll=loc_coords, limit=limit)
        responses += response['businesses']  # list
    return responses;

'''
# pass in a list of tuples for locations. Default
# category_filter is a list of category namesis SF and San Jose
def get_results_from_locations(category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)], num_of_results=40 , limit = 20):
    # parse location if two locations given
    if len(coords) == 2:
        loc1 = coords[0]
        loc2 = coords[1]
        long = (loc1[0] + loc2[0])/2;
        lat = (loc1[1] + loc2[1])/2;
        loc_coords = str(long) + "," + str(lat);
        location = get_location_from_coordinates(long, lat)
        print (loc_coords, location)

    elif len(coords) == 1:
        loc1 = coords[0];
        long = loc1[0];
        lat = loc1[1];
        loc_coords = str(long) + "," + str(lat);
        location = get_location_from_coordinates(long, lat);
        print (loc_coords, location)

    else:
        raise Exception("Please provide no more than two location coordinate sets");
    iterations = math.ceil(num_of_results / limit);

    aliases = ''
    for category in category_filter:
        aliases += category_name_to_alias_dict[category] + ','
    aliases = aliases[:-1]  # strip the last comma

    responses = [];

    for i in range(iterations):
        time.sleep(.3)
        response = yelp_api.search_query(category_filter=aliases, location=location, offset=limit*i, cll=loc_coords, limit=limit)
        responses += response['businesses']  # list
    return responses;

'''
def get_yelp_data(list_businesses):
    list_yelp_data = [];
    for bus in list_businesses:
        list_yelp_data.append(YelpData(bus));
    return list_yelp_data


def get_restaurant_vectors_by_query(category_filter, coords):
    list_businesses = get_results_from_locations(category_filter, coords=coords)
    return get_yelp_data(list_businesses)

if __name__ == '__main__':
    results = get_results_from_locations(40)
    #pp.pprint(results);
  #  print(len(results))

