from yelpapi import YelpAPI
import pprint as pp
import math;
import time;
import urllib;
import json;

consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'

google_places_key="AIzaSyBrElDm-bOxHup93M1QLfWXYjpYYoReGjg"

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)

# deprecated
'''
def get_results_from_location(num_of_results, location="37.77493,-122.419415", limit = 20):
    iterations = math.ceil(num_of_results / limit);
    responses = [];
    print(iterations)
    for i in range(iterations):
        time.sleep(.5)
        response = yelp_api.search_query(category_filter='italian', location="SanFrancisco", offset=limit*i, cll=location, limit=limit)
        responses += response['businesses'] #list
    return responses;
'''



def get_location_from_coordinates(long,lat) -> str:
    LOCATION = str(long) + "," + str(lat)
    RADIUS = 1;
    MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&key=%s') % (LOCATION, RADIUS, google_places_key)
    #grabbing the JSON result
    response = urllib.request.urlopen(MyUrl)
    jsonRaw = response.read().decode("utf-8")
    jsonData = json.loads(jsonRaw)
    # parse for location name i.e. San Francisco
    location_name = jsonData['results'][0]['vicinity']
    return location_name



# pass in a list of tuples for locations. Default is SF and San Jose
def get_results_from_locations(num_of_results, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)], limit = 20):
    # parse location if two locations given

    loc_coords = "";
    location = "";
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
    responses = [];
    for i in range(iterations):
        time.sleep(.5)
        response = yelp_api.search_query(category_filter='italian', location=location, offset=limit*i, cll=loc_coords, limit=limit)
        responses += response['businesses'] #list
    return responses;



if __name__ == '__main__':
    results = get_results_from_locations(40)
    #pp.pprint(results);
  #  print(len(results))

