"""SCRIPT TO UPLOAD CATEGORY LIST TO MySQL DB"""
# Created by: Jeet Nagda
import json

#reading in the data
with open('categories.json') as data_file:    
    data = json.load(data_file)

# list of final categories to upload, will be adding tuples
list_of_categories = []
# Set of valid categories to explore, seed category is 'restaurants'
valid_categories = set(['restaurants'])

# first pass, get all children of 'restaurants' and add them as valid categories
for item in data:
    if 'restaurants' in item['parents']:
        if 'country_whitelist' not in item.keys() or 'US' in item['country_whitelist']:
            valid_categories.add(item['alias'])
            list_of_categories.append((item['title'],item['alias']))

# second pass, get all children of valid categories and add to list_of_categories if not already in there
for item in data:
    if len(item['parents']) > 0 and set(item['parents']).issubset(valid_categories):
        if ('country_whitelist' not in item.keys()) or ('US' in item['country_whitelist']):
            temp_item = (item['title'],item['alias'])
            if temp_item not in list_of_categories:
                list_of_categories.append(temp_item)

# TODO: Possible effeciency increase by hasing list_of_categories as {Key (string) CategoryName: Value (tuple) data}
# Debug Print lines:
# print("LEN OF CATEGORY LIST:",len(list_of_categories))
# for x in sorted(list_of_categories):
#      print(x)

# Inserting category list into MySQL Database
import mysql.connector

config = {
    'user': 'ucifooddy',
    'password': 'ucifooddy',
    'host': 'fooddy.cxayrrely1fe.us-west-2.rds.amazonaws.com',
    'database': 'fooddy2.0',
    # 'cursorclass' : 'MySQLdb.cursors.SSCursor',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)

insert_sql = 'INSERT IGNORE INTO Categories(category_name,category_alias) VALUES (%s,%s)'

curr = cnx.cursor()
curr.executemany(insert_sql,list_of_categories)
cnx.commit()
curr.close()
cnx.close()