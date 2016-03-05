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

if __name__ == '__main__':
    results = get_results_from_location(40 , location="37.77493,-122.419415")
    pp.pprint(results);
    print(len(results))