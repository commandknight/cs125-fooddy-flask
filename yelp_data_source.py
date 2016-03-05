from yelpapi import YelpAPI
import pprint as pp
import math;
import time;

consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)
cll_sf = "37.77493,-122.419415"

# response = yelp_api.search_query(category_filter='italian', location="SanFrancisco", offset=0, limit=20)


def get_results_from_location(num_of_results, location="37.77493,-122.419415", limit = 20):
    iterations = math.ceil(num_of_results / limit);
    responses = [];
    print(iterations)
    for i in range(iterations):
        time.sleep(.5)
        response = yelp_api.search_query(category_filter='italian', location="SanFrancisco", offset=limit*i, cll=location, limit=limit)
        responses += response['businesses'] #list
    return responses;



# pass in a list of tuples for locations. Default is SF and Daly City
def get_results_from_locations(num_of_results, locations=[(37.77493,-122.419415) , (37.3382, 121.8863)], limit = 20):
    # parse location if two locations given
    loc_coords = "";
    if len(locations) == 2:
        loc1 = locations[0]
        loc2 = locations[1]
        loc_coords = str(loc1[0] + loc2[0]/2) + "," + str(loc1[1] + loc2[1]/2);
        print (loc_coords)
    elif len(locations) == 1:
        loc1 = locations[0];
        loc_coords = str(loc1[0]) + "," + str(loc1[1]);

    else:
        raise Exception("Please provide no more than two location coordinate sets");

    iterations = math.ceil(num_of_results / limit);
    responses = [];
    print(iterations)
    for i in range(iterations):
        time.sleep(.5)
        response = yelp_api.search_query(category_filter='italian', location="SanFrancisco", offset=limit*i, cll=loc_coords, limit=limit)
        responses += response['businesses'] #list
    return responses;




if __name__ == '__main__':
    results = get_results_from_locations(40)
    pp.pprint(results);
  #  print(len(results))

