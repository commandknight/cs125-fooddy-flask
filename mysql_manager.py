import mysql.connector

config = {
    'user': 'jeet',
    'password': 'paper2mate',
    'host': 'cs175redditproject.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'database': 'cs175reddit',
    # 'cursorclass' : 'MySQLdb.cursors.SSCursor',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)

def get_test_data():
    curr = cnx.cursor()
    curr.execute('SELECT * FROM TestTable')
    return curr.fetchall()


def close_connection():
    """
    Function to close connection to MySQL Database
    :return: None
    """
    cnx.close()