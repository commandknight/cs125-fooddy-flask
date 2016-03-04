import mysql.connector

config = {
    'user': 'ucifooddy',
    'password': 'ucifooddy',
    'host': 'fooddy.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'database': 'fooddy',
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