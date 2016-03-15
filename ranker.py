import yelp_data_source as ydp;
import numpy as np
from scipy import spatial
import mysql_manager as mm;



# coords is a list of long lat tuples. (1 or 2))
# category filter is a list of string categories
# returns a list of YelpData sorted by the most similar to the least
def get_ranking_by_cosine(username, category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)]):
    list_yelp_data = ydp.get_restaurant_vectors_by_query(category_filter,coords);
    user_weight_vec = mm.get_user_weights_vector(username);
    for yelp_data in list_yelp_data:
        yelp_data.cosine_sim = 1 - spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector);
        # np.rad2deg(np.arccos(1- spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector))) for degrees
    # sots by ascending order
    list_yelp_data.sort(key=lambda x: x.cosine_sim);
    return list_yelp_data



# todo: finish implementation
def get_results_probabilistic(username, category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)]):
    list_yelp_data = ydp.get_restaurant_vectors_by_query(category_filter,coords);
    user_weight_vec = mm.get_user_weights_vector(username);
    sum_weights = np.sum(user_weight_vec);
    for yelp_data in list_yelp_data:
        yelp_data.cosine_sim = np.dot(user_weight_vec, yelp_data.restaurant_vector)/sum_weights; # change variable name later

    # random number generator to sort.
    return list_yelp_data





