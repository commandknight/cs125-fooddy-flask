"""
Created by Jeet Nagda
import mysql_manager as mm
result = mm.get_list....
"""

from datetime import datetime
from decimal import Decimal

import numpy as np
import pymysql as mysql

# Configuration for mysql database
config = {
    'user': 'ucifooddy',
    'password': 'ucifooddy',
    'host': 'fooddy.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'fooddy2.0',
    'raise_on_warnings': True
}

cnx = mysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['password'],
                    db=config['database'])


# cnx = mysql.connector.connect(**config)


def get_category_dict():
    """
    function to make dictionary of category names -> id
    :return: Dictionary{Key: String(Category_Name), Value: Int(Category_ID)}
    """
    category_dict = {}
    print("making dict")
    category_names = get_list_of_category_names()
    for idx, tup in enumerate(category_names):
        category_dict[tup[0]] = idx
    return category_dict


def get_idx_to_category_dict():
    idx_category_dict = {}
    category_names = get_list_of_category_names()
    for idx, category_name_tuple in enumerate(category_names):
        idx_category_dict[idx] = category_name_tuple[0]
    return idx_category_dict


def get_category_name_to_alias_dict():
    """
    function to make dictionary of category name -> alias
    :return: Dictionary{Key: String(category_name), Value: String category_alias}
    """
    print("making alias dict")
    curr = cnx.cursor()
    curr.execute('SELECT category_alias, category_name From Categories')
    result = curr.fetchall()
    curr.close()
    name_to_alias_dict = {}
    for category_alias, category_name in result:
        name_to_alias_dict[category_name] = category_alias
    return name_to_alias_dict


def get_list_categories_for_profile_edit(user_name):
    """
    Function that returns tuple of (Category_Name,liked)
    :param user_name: username to get liked categories of
    :return: List(Tuple(String,Boolean)) ex: ('Italian',True)
    """
    category_names = get_list_of_category_names()
    categories_liked = get_list_of_category_names_user_likes(username=user_name)
    result = []
    for category in category_names:
        result.append((category[0], True if category[0] in categories_liked else False))
    return result


def get_list_of_category_names():
    """
    Function to return list of category names as list(tuples(string,))
    :return: category names as list(tuples(string,))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_name From Categories ORDER BY category_name ASC')
    result = curr.fetchall()
    curr.close()
    return result


def get_list_of_category_alias():
    """
    Function to return list of category aliases names as list(tuples(string,))
    :return: category alaises list(tuples(string,))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_alias FROM Categories')
    result = curr.fetchall()
    non_tuple_list = [x[0] for x in result]
    curr.close()
    return non_tuple_list


def get_list_of_category_names_user_likes(username):
    """
    Function to get list of category names that the user likes
    :param username of profile
    :return: list(tuples(string,))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_name FROM UserProfile,UserWeights,Categories '
                 'WHERE UserWeights.category_id = Categories.category_id AND '
                 'UserProfile.user_name = UserWeights.user_name '
                 'AND UserWeights.weight > 0.0'
                 'AND UserProfile.user_name = %s', (username,))
    result = curr.fetchall()
    curr.close()
    return [x[0] for x in result]


def get_category_weights_and_last_visit_for_user(username):
    """
    Function to get list of category names and weights, note need to cast tuple Decimal as float
    :param username of profile
    :return: list(tuples(string,Decimal))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_name,weight,last_visit FROM UserProfile,UserWeights,Categories '
                 'WHERE UserWeights.category_id = Categories.category_id AND '
                 'UserProfile.user_name = UserWeights.user_name '
                 'AND UserWeights.weight > 0.0'
                 'AND UserProfile.user_name = %s', (username,))
    result = curr.fetchall()
    curr.close()

    return result


def get_number_of_categories():
    """
    Function to get number of categories table
    :return: int
    """
    curr = cnx.cursor()
    curr.execute('SELECT COUNT(*) FROM Categories')
    result = curr.fetchone()
    curr.close()
    return result[0]


def is_login_valid(username, password):
    """
    Function to check if given login information is valid
    :param username: user_names as profile, used as PK
    :param password: password to check if valid
    :return: Boolean response if login is accepted or not
    """
    curr = cnx.cursor()
    curr.execute('SELECT password FROM UserProfile WHERE user_name = %s', (username,))
    password_tmp = curr.fetchone()
    curr.close()
    if password_tmp is None:
        return False
    return password == password_tmp[0]


def insert_category(category_name, category_alias):
    """
    Function to insert new category record
    :param category_name: String formal name of category to insert Ex: "Italian"
    :param category_alias: String alias used by Yelp API to search Ex: "italian"
    :return: None
    """
    curr = cnx.cursor()
    curr.execute('INSERT IGNORE INTO Categories(category_name,category_alias)', (category_name, category_alias))
    cnx.commit()
    curr.close()


def insert_new_user_profile(username, password):
    """
    Function to insert new user_profile into database
    :param username: String PK user_name to insert
    :param password: String Password of new user
    :return: None
    """
    curr = cnx.cursor()
    curr.execute('INSERT IGNORE INTO UserProfile(user_name,password) VALUES (%s,%s)'
                 'ON DUPLICATE KEY UPDATE password = %s', (username, password, password))
    cnx.commit()
    curr.close()


def init_category_weight_vector_for_user(user_name, init_weight):
    """
    Function to init the user vector
    :param user_name: user_name to init
    :param init_weight: the weight to init the vector
    :return:
    """
    category_names = get_list_of_category_names()
    for category in category_names:
        init_category_weight_if_not_present(user_name, category[0], init_weight)


def update_weight_datetime_of_categories_for_user(user_name, list_of_weights, list_of_categories):
    sql_update_last_visit = 'UPDATE UserWeights SET weight = %s, last_visit = NOW() WHERE user_name = %s and category_id = ' \
                            '(SELECT category_id FROM Categories WHERE category_name = %s)'
    curr = cnx.cursor()
    for index in range(len(list_of_weights)):
        curr.execute(sql_update_last_visit, (list_of_weights[index], user_name, list_of_categories[index]))
    cnx.commit()
    curr.close()


def init_category_weight_if_not_present(user_name, category_name, weight):
    """
    Function to INSERT or IGNORE UserWeight for given category_name and weight
    :param user_name: string UserName of UserWeight to update/insert
    :param category_name: String alias of category weight to update
    :param weight: Double of the weight to insert
    :return: None
    """
    curr = cnx.cursor()
    sql_insert_update_UserWeight = 'INSERT IGNORE INTO UserWeights(user_name,category_id,weight) ' \
                                   'VALUES (%s,(SELECT category_id FROM Categories WHERE category_name = %s),%s)'
    curr.execute(sql_insert_update_UserWeight, (user_name, category_name, weight))
    cnx.commit()
    curr.close()


def update_category_alias_weight(user_name, category_alias, weight):
    """
    Function to INSERT or UPDATE UserWeight for given category_alias and weight
    :param user_name: string UserName of UserWeight to update/insert
    :param category_alias: String alias of category weight to update
    :param weight: Double of the weight to insert
    :return: None
    """
    curr = cnx.cursor()
    sql_insert_update_UserWeight = 'INSERT IGNORE INTO UserWeights(user_name,category_id,weight) ' \
                                   'VALUES (%s,(SELECT category_id FROM Categories WHERE category_alias = %s),%s) ' \
                                   'ON DUPLICATE KEY UPDATE weight = %s last_visit = NOW()'
    curr.execute(sql_insert_update_UserWeight, (user_name, category_alias, weight, weight))
    cnx.commit()
    curr.close()


def update_category_name_weight(user_name, category_name, weight):
    """
    Function to INSERT or UPDATE UserWeight for given category_alias and weight
    :param user_name: string UserName of UserWeight to update/insert
    :param category_alias: String alias of category weight to update
    :param weight: Double of the weight to insert
    :return: None
    """
    curr = cnx.cursor()
    sql_insert_update_UserWeight = 'INSERT IGNORE INTO UserWeights(user_name,category_id,weight) ' \
                                   'VALUES (%s,(SELECT category_id FROM Categories WHERE category_name = %s),%s) ' \
                                   'ON DUPLICATE KEY UPDATE weight = %s'
    curr.execute(sql_insert_update_UserWeight, (user_name, category_name, weight, weight))
    cnx.commit()
    curr.close()


def reset_user_profile(user_name):
    """
    Function to reset user profile for a given user name
    :param user_name: String of user to reset
    :return: None
    """
    curr = cnx.cursor()
    sql_reset_user = 'DELETE FROM UserWeights WHRE user_name = %s'
    curr.execute(sql_reset_user, (user_name,))
    cnx.commit()
    curr.close()


def get_user(user_name):
    """
    Function get user_name given id
    :param id:
    :return: tuple(String username, String password)
    """
    curr = cnx.cursor()
    curr.execute('SELECT user_name, password FROM UserProfile WHERE user_name = %s', (user_name,))
    result = curr.fetchone()
    curr.close()
    return result

def get_user_weights_vector(username):
    """
    Function to get user_vector from DB
    :param username: user_name of vector to get
    :return: Array(double) user_vector
    """
    user_weight_vec = np.zeros(num_categories)
    weights = get_category_weights_and_last_visit_for_user(username)
    for tup in weights:
        user_weight_vec[category_dict[tup[0]]] = tup[1]
    if np.count_nonzero(user_weight_vec) == 0:
        raise Exception("user weight vector is zero~!!!")
    return user_weight_vec


def get_user_weights_vector_and_last_update_vector(username):
    """
    Function to get user_vector from DB
    :param username: user_name of vector to get
    :return: Array(double) user_vector
    """
    user_weight_vec = np.zeros(num_categories)

    weights = get_category_weights_and_last_visit_for_user(username)

    last_update_vector = np.zeros(num_categories)  # last update in days
    now = datetime.utcnow()
    for tup in weights:
        cat_name = tup[0]
        weight = tup[1]
        last_update_datetime = tup[2]
        user_weight_vec[category_dict[cat_name]] = weight
        if last_update_datetime == None:
            last_update_vector[category_dict[cat_name]] = 0  # 0 means we wont decay it
        else:
            num_days = (now - last_update_datetime).days;
            last_update_vector[category_dict[cat_name]] = num_days;

    if np.count_nonzero(user_weight_vec) == 0:
        raise Exception("user weight vector is zero~!!!")
    return user_weight_vec, last_update_vector


def insert_business_or_ignore(business_obj, list_of_categories_alias):
    """
    Function that will insert business into Business Table if not exists.
    Then inserts the associated category_alias and business_id in relational table
    :param business_obj: YelpData Object
    :param list_of_categories: category aliases that the business belongs to
    :param user_name: user_name of user
    :return: None
    """
    business_name = business_obj.restaurant_info.__getattribute__('name')
    business_id = business_obj.restaurant_info.__getattribute__('id')
    curr = cnx.cursor()
    sql_insert_new_business = 'INSERT IGNORE INTO Businesses (business_id,business_name) VALUES (%s,%s,%s)'
    curr.execute(sql_insert_new_business, (business_id, business_name))
    sql_insert_business_category = 'INSERT IGNORE INTO Business_Category (business_id,category_id) VALUES (%s,' \
                                   '(SELECT category_id FROM Categories WHERE category_alias = %s))'
    for category_alias in list_of_categories_alias:
        curr.execute(sql_insert_business_category, (business_id, category_alias))
    cnx.commit()
    curr.close()


def insert_visit_and_update_categories_for_business(business_id, list_of_categories, user_name, rating):
    """
    Function to insert a visit to a business_id for a given user_name and datetime string
    :param business_id: id of the business that user_name visisted
    :param date_time_string: the datetime string that the visit occured
    :param user_name: user_name of the user that made the visit
    :return: None
    """
    sql_insert_visit = 'INSERT IGNORE INTO Business_Log (business_id,user_name,visit,rating) VALUES(%s,%s,NOW(),%s) ' \
                       'ON DUPLICATE KEY UPDATE visit = NOW(), rating = %s'
    curr = cnx.cursor()
    curr.execute(sql_insert_visit, (business_id, user_name, rating, rating))
    sql_insert_business_category = 'INSERT IGNORE INTO Business_Category (business_id,category_id) VALUES (%s,' \
                                   '(SELECT category_id FROM Categories WHERE category_name = %s))'
    for category_alias in list_of_categories:
        curr.execute(sql_insert_business_category, (business_id, category_alias))
    cnx.commit()
    update_category_weights_by_visit(user_name, list_of_categories)
    curr.close()


def update_user_vector(user_name, new_user_vector):
    """
    Method to update the user weights with new user_vector
    :param user_name: user_name of vector to update
    :param new_user_vector: vector 1D array with idx as order of get_category_names, and value category_weight
    :return: None
    """
    lookup = get_idx_to_category_dict()
    for idx, category_weight in enumerate(new_user_vector):
        category_name = lookup[idx]
        update_category_name_weight(user_name, category_name, category_weight)


def update_category_weights_by_visit(username, list_categories):
    """
    Update categories based on where the user_name has visited
    :param username: user_name of the user to update
    :param list_categories: categories of the visit
    :return: None
    """

    returns = get_user_weights_vector_and_last_update_vector(username) # has weight vector and a vector containing # of days since last update
    user_vector = returns[0]
    list_weights = []

    for category in list_categories:
        if category in set_categories:
            category_index = category_dict[category]
            current_weight = user_vector[category_index]
            print(current_weight)
            new_weight = current_weight + (
                .75 / current_weight) + .5  # .75 is multiplicative constant for original boost,
            #  .5 ensuring is constant increase. necessary for good probabilistic returns
            new_weight = float(round(Decimal(new_weight),3))
            list_weights.append(new_weight)
    update_weight_datetime_of_categories_for_user(username, list_weights, list_categories)
    print(list_categories)
    print(list_weights)

# Todo: degenerate categories by looking at the last visited time.
# Need to get the last time updated/visited category attribute from DB. jeet pls.
# Planning to use this at the start of every user login so they can have the most updated vector
def degenerate_categories(username):
    days_til_decay = 5
    returns = get_user_weights_vector_and_last_update_vector(username)  # has weight vector and a vector containing # of days since last update
    user_vector = returns[0]
    last_update_vector = returns[1]
    num_of_decay = np.floor(last_update_vector/days_til_decay)
    list_categories = []
    list_new_weights = []
    for idx, category_weight in enumerate(user_vector):
        # if we use latter: floor (time_from_last_visited / decay_threshold) i.e. 3 days ago / decay in 3 days
        # for loop the decay for that category.
        if num_of_decay[idx] == 0:
            continue;
        decayed_weight = category_weight;
        for j in range(num_of_decay[idx]): # number of times we decay the weight.
            decayed_weight = decayed_weight - (.75 / decayed_weight) - .5
            if decayed_weight < .15:  # we will set .15 as the start weight.
                decayed_weight = .15
                break;

        decayed_weight = float(round(Decimal(decayed_weight),3))
        list_categories.append(idx_to_category_dict[idx]);
        list_new_weights.append(decayed_weight);

        # update the whole vector by removing old one and replacing with new one.
        # less db calls? or just update it all at once
    update_weight_datetime_of_categories_for_user(username, list_new_weights, list_categories);


def close_connection():
    """
    Function to close connection to MySQL Database
    :return: None
    """
    cnx.close()

# gets the rating value. even though it is blacklist right now, for demo we will use rating
def get_rating_by_business_id(user_name, business_id):
    """
    :param user_name:
    :param business_id:
    :return: 0 or 1 indicaitng blacklisted or not
    """
    curr = cnx.cursor()
    sql_blacklist_status = 'SELECT rating FROM Business_Log WHERE user_name = %s and business_id = %s'
    curr.execute(sql_blacklist_status, (user_name, business_id))
    result = curr.fetchone()
    curr.close()
    if result == None:
        return 1
    return result[0]


# do not use if we switch back to rating

def get_visited_businesses_by_username(user_name):
    """
    :param user_name:
    :return: list of tuples of (business_ids, )
    """
    curr = cnx.cursor()
    curr.execute('SELECT business_id FROM Business_Log WHERE user_name = %s', (user_name,))
    result = curr.fetchall()
    curr.close()
    return result


# TODO:
def get_user_rating_for_resturant(user_name, resturant_id):
    pass


def add_visit_to_business_log(user_name, resturant_id, is_blacklisted, list_of_categories):
    pass



# CONSTANTS! #####
category_dict = get_category_dict()
num_categories = len(category_dict)
category_name_to_alias_dict = get_category_name_to_alias_dict()
idx_to_category_dict = get_idx_to_category_dict()
set_aliases = set(category_name_to_alias_dict.values())
set_categories = set(category_name_to_alias_dict.keys())