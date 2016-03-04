import mysql.connector

config = {
    'user': 'ucifooddy',
    'password': 'ucifooddy',
    'host': 'fooddy.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'database': 'fooddy',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)

def get_list_of_category_names():
    curr = cnx.cursor()
    curr.execute('SELECT category_name From Categories')
    result = curr.fetchall()
    curr.close()
    return result


def get_list_of_category_alias():
    curr = cnx.cursor()
    curr.execute('SELECT category_alias FROM Categories')
    result = curr.fetchall()
    curr.close()
    return result


def get_list_of_category_names_user_likes(username):
    curr = cnx.cursor()
    curr.execute('SELECT category_name FROM Categories,UserProfile,UserWeights '
                 'WHERE C'
                 'ategories.category_id = UserWeights.category_id '
                 'AND UserWeights.weight > 0 '
                 'AND UserProfile.username = %s',(username))
    result = curr.fetchall()
    curr.close()
    return result


def get_category_weights_for_user(username):
    curr = cnx.cursor()
    curr.execute('SELECT category_name,weight FROM Categories,UserWeights,UserProfile '
                 'WHERE Categories.category_id = UserWeights.category_id AND'
                 'UserProfile.user_name = UserWeights.user_name '
                 'AND UserWeight.weight > 0.0'
                 'AND UserProfile.username = %s',(username))
    result = curr.fetchall()
    curr.close()
    return result


def get_number_of_categories():
    curr = cnx.cursor()
    curr.execute('SELECT COUNT(*) FROM Categorires')
    result = curr.fetchone()
    curr.close()
    return result


def close_connection():
    """
    Function to close connection to MySQL Database
    :return: None
    """
    cnx.close()