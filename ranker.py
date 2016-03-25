import numpy as np
from scipy import spatial

import mysql_manager as mm;
import yelp_data_source as ydp;


# coords is a list of long lat tuples. (1 or 2))
# category filter is a list of string categories
# returns a list of YelpData sorted by the most similar to the least
def get_ranking_by_probabilistic_cosine(username, coords=[(33.6694, -117.8231)], num_results=80):

    list_yelp_data = ydp.get_restaurant_vectors_by_query(coords, num_results)
    user_weight_vec = mm.get_user_weights_vector(username)
    list_cosine_sims = []
    for idx,yelp_data in enumerate(list_yelp_data):
        yelp_data.cosine_sim = np.dot(user_weight_vec, yelp_data.restaurant_vector); # try dot product for more bias i think. add one smoothng can be done for dot product
        #yelp_data.cosine_sim = 1 - spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector)
        print(yelp_data.cosine_sim, yelp_data.restaurant_info.name)
        list_cosine_sims.append(yelp_data.cosine_sim + .1)
        # np.rad2deg(np.arccos(1- spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector))) for degrees
    # sorts restaurants by probabilistics by their cosine similarity in an attempt to keep things interesting.
    # print(list_cosine_sims)
    # print(user_weight_vec)
    if len(list_yelp_data) == 0:
        return list_yelp_data
    list_yelp_data = np.random.choice(list_yelp_data, len(list_yelp_data), p=list_cosine_sims/np.sum(list_cosine_sims), replace=False).tolist()
    return list_yelp_data



def get_nearby_restaurants(username, coords, radius=300, num_results=80):
    """
    :param username:
    :param coords:
    :param radius:
    :param num_results:
    :return: returns a empty list if no restaurants near you.
    """
    list_yelp_data = ydp.get_restaurant_vectors_by_query(coords, num_results, radius=radius)
    user_weight_vec = mm.get_user_weights_vector(username)
    list_cosine_sims = []
    for idx,yelp_data in enumerate(list_yelp_data):
        yelp_data.cosine_sim = np.dot(user_weight_vec, yelp_data.restaurant_vector); # try dot product for more bias i think. add one smoothng can be done for dot product
        #yelp_data.cosine_sim = 1 - spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector)
        print(yelp_data.cosine_sim, yelp_data.restaurant_info.name)
        list_cosine_sims.append(yelp_data.cosine_sim + .1)
        # np.rad2deg(np.arccos(1- spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector))) for degrees
    # sorts restaurants by probabilistics by their cosine similarity in an attempt to keep things interesting.
    # print(list_cosine_sims)
    # print(user_weight_vec)
    if len(list_yelp_data) == 0:
        return list_yelp_data
    list_yelp_data = np.random.choice(list_yelp_data, len(list_yelp_data), p=list_cosine_sims/np.sum(list_cosine_sims), replace=False).tolist()
    return list_yelp_data

