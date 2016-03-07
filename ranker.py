import yelp_data_source as ydp;
import numpy as np
from scipy import spatial
import mysql_manager as mm;


def get_user_weights_vector(username):
    user_weight_vec = np.zeroes(ydp.num_categories);
    weights = mm.get_category_weights_for_user(username)
    for tup in weights:
        user_weight_vec[ydp.category_dict[tup[0]]] = tup[1]
    if (np.count_nonzero(user_weight_vec) == 0):
        raise Exception("user weight vector is zero~!!!")
    return user_weight_vec

# coords is a list of long lat tuples. (1 or 2))
# category filter is a list of string categories
# returns a list of YelpData
def get_ranking_by_cosine(username, category_filter, coords=[(37.77493,-122.419415) , (37.3382, -121.8863)]):
    list_yelp_data = ydp.get_restaurant_vectors_by_query(category_filter,coords);
    user_weight_vec = get_user_weights_vector(username);
    for yelp_data in list_yelp_data:
        yelp_data.cosine_sim = spatial.distance.cosine(user_weight_vec, yelp_data.restaurant_vector)
    # sots by ascending order
    list_yelp_data.sort(key=lambda x: x.cosine_sim);
    return list_yelp_data





