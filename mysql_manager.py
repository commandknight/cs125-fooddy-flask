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

def is_login_valid(username,password):
    curr = cnx.cursor()
    curr.execute('SELECT password FROM UserProfile WHERE user_name = %s',(username))
    password_tmp = curr.fetchone()
    curr.close()
    if password == password_tmp:
        return True
    else:
        return False


def insert_category(category_name,category_alias):
    curr = cnx.cursor()
    curr.execute('INSERT INTO Categories(category_name,category_alias)',(category_name,category_alias))
    curr.close()

# TODO: Insert new userProfile
def insert_user_profile(username,password):
    curr = cnx.cursor()
    curr.execute('INSERT INTO UserProfile(user_name,password)',(username,password))
    curr.close()

# TODO: Insert/Update Category Weight
def update_category_weight(category_alias,weight):
    curr = cnx.cursor()
    sql_get_category_id = 'SELECT category_id FROM Categories WHERE category_alias = %s'
    category_id = curr.execute(sql_get_category_id,(category_alias)).fetchone()
    sql_insert_update = ''
    curr.execute(sql_insert_update,(category_id,weight))
    curr.close()


def close_connection():
    """
    Function to close connection to MySQL Database
    :return: None
    """
    cnx.close()