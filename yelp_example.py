from yelpapi import YelpAPI
import argparse
from pprint import pprint

print("START")

consumer_key = 'EXZNRAR-epLUvS7LnuwqNg'
consumer_secret = 'JTZY_0nE8ohfazCK-e_hP_aHhDs'
token = 'Sa67MrlQ3hoVCr3Wsn2rfU9-kPPQ40Q_'
token_secret = '8Xyb1WAJpRW_TJFomJb3eom3e4w'   


yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)
cll_sf="37.77493,-122.419415"


print('\n-------------------------------------------------------------------------\n')

response = yelp_api.search_query(category_filter='tuscan',location="SanFrancisco",cll=cll_sf, sort=2, limit=5)
#response = yelp_api.search_query(category_filter='Calabrian', bounds='37.678799,-123.125740|37.832371,-122.356979', limit=5)
pprint(response)

print('\n-------------------------------------------------------------------------\n')



