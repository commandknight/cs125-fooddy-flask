import yelp_data_source as ydp;
import numpy as np
from scipy import spatial
import mysql_manager as mm;
from numpy.random import random_sample




# coords is a list of long lat tuples. (1 or 2))
# category filter is a list of string categories
# returns a list of YelpData sorted by the most similar to the least
def get_ranking_by_probabilistic_cosine(username, category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)], num_results=60):
    list_yelp_data = ydp.get_restaurant_vectors_by_query(category_filter,coords, num_results);
    user_weight_vec = mm.get_user_weights_vector(username);
    list_cosine_sims = [];
    for idx,yelp_data in enumerate(list_yelp_data):
        # yelp_data.cosine_sim = np.dot(user_weight_vec, yelp_data.restaurant_vector); # try dot product for more bias i think. add one smoothng can be done for dot product
        yelp_data.cosine_sim = 1 - spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector);
        list_cosine_sims[idx] = yelp_data.cosine_sim + .1;
        # np.rad2deg(np.arccos(1- spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector))) for degrees
    # sorts restaurants by probabilistics by their cosine similarity in an attempt to keep things interesting.
    list_yelp_data = np.random.choice(list_yelp_data, num_results, p=list_cosine_sims, replace=False).tolist()
    return list_yelp_data


