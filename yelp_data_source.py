from yelpapi import YelpAPI
import json
consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)
cll_sf="37.77493,-122.419415"

def get_top_ten_results(location="37.77493,-122.419415"):
    response = yelp_api.search_query(category_filter='italian',location="SanFrancisco",cll=location, sort=2, limit=20)
    return response['businesses']


