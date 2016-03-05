import json
from pprint import pprint

with open('categories.json') as data_file:    
    data = json.load(data_file)

list_of_categories = []


for item in data:
    if 'restaurants' in item['parents']:
        if 'country_whitelist' not in item.keys() or 'US' in item['country_whitelist']:
            print(item['title'])
            list_of_categories.append((item['title'],item['alias']))


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

insert_sql = 'INSERT INTO Categories(category_name,category_alias) VALUES (%s,%s)'

curr = cnx.cursor()
curr.executemany(insert_sql,list_of_categories)
cnx.commit()
curr.close()
cnx.close()