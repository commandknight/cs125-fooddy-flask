"""
Created by Jeet Nagda
To Use: please import right before you call it, and close immediately after finish
import mysql_manager as mm
result = mm.get_list....
"""

import mysql.connector

# Configuration for mysql database
config = {
    'user': 'ucifooddy',
    'password': 'ucifooddy',
    'host': 'fooddy.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'database': 'fooddy2.0',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)


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
        result.append((category[0],True if category[0] in categories_liked else False))
    return result


def get_list_of_category_names():
    """
    Function to return list of category names as list(tuples(string,))
    :return: category names as list(tuples(string,))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_name From Categories')
    result = curr.fetchall()
    curr.close()
    return result


def get_category_dict():
    """
    function to make dictionary of category names -> id
    :return: Dictionary{Key: String(Category_Name), Value: Int(Category_ID)}
    """
    category_dict = {}
    print("making dict")
    result = get_list_of_category_names()
    for idx,tup in enumerate(result):
        category_dict[tup[0]] = idx
    return category_dict


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
    for category_alias,category_name in result:
        name_to_alias_dict[category_name] = category_alias
    return name_to_alias_dict


def get_list_of_category_alias():
    """
    Function to return list of category aliases names as list(tuples(string,))
    :return: category alaises list(tuples(string,))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_alias FROM Categories')
    result = curr.fetchall()
    curr.close()
    return result


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
                 'AND UserProfile.user_name = %s',(username,))
    result = curr.fetchall()
    curr.close()
    return [x[0] for x in result]


def get_category_weights_for_user(username):
    """
    Function to get list of category names and weights, note need to cast tuple Decimal as float
    :param username of profile
    :return: list(tuples(string,Decimal))
    """
    curr = cnx.cursor()
    curr.execute('SELECT category_name,weight FROM UserProfile,UserWeights,Categories '
                 'WHERE UserWeights.category_id = Categories.category_id AND '
                 'UserProfile.user_name = UserWeights.user_name '
                 'AND UserWeights.weight > 0.0'
                 'AND UserProfile.user_name = %s',(username,))
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


def is_login_valid(username,password):
    """
    Function to check if given login information is valid
    :param username: user_names as profile, used as PK
    :param password: password to check if valid
    :return: Boolean response if login is accepted or not
    """
    curr = cnx.cursor()
    curr.execute('SELECT password FROM UserProfile WHERE user_name = %s',(username,))
    password_tmp = curr.fetchone()
    curr.close()
    if password_tmp is None:
        return False
    return password == password_tmp[0]


def insert_category(category_name,category_alias):
    """
    Function to insert new category record
    :param category_name: String formal name of category to insert Ex: "Italian"
    :param category_alias: String alias used by Yelp API to search Ex: "italian"
    :return: None
    """
    curr = cnx.cursor()
    curr.execute('INSERT IGNORE INTO Categories(category_name,category_alias)',(category_name,category_alias))
    cnx.commit()
    curr.close()


def insert_new_user_profile(username,password):
    """
    Function to insert new user_profile into database
    :param username: String PK user_name to insert
    :param password: String Password of new user
    :return: None
    """
    curr = cnx.cursor()
    curr.execute('INSERT IGNORE INTO UserProfile(user_name,password) VALUES (%s,%s)'
                 'ON DUPLICATE KEY UPDATE password = %s',(username,password,password))
    cnx.commit()
    curr.close()


def init_category_weight_if_not_present(user_name,category_name,weight):
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
    curr.execute(sql_insert_update_UserWeight,(user_name,category_name,weight))
    cnx.commit()
    curr.close()


def update_category_alias_weight(user_name,category_alias,weight):
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
    curr.execute(sql_insert_update_UserWeight,(user_name,category_alias,weight,weight))
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


def close_connection():
    """
    Function to close connection to MySQL Database
    :return: None
    """
    cnx.close()