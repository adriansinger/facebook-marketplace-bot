import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from price_comparison_tool import get_login_creds

full_creds = get_login_creds()
sql_user = full_creds[2]
sql_password = full_creds[3]

db = mysql.connector.connect(
	host = 'localhost',
	user = sql_user,
	passwd = sql_password,
	database = 'facebook_marketplace_items'
	)

mycursor = db.cursor()

price_query = """
			  SELECT price
			  FROM items3
              WHERE category = 'Smoker'
			  """

title_price_query = """
					SELECT itemID, price
					FROM items3
                    WHERE category = 'Smoker'
					"""

 
def view_data(cursor):
	view_query = """
                SELECT title, urlID 
                FROM items3 
                WHERE category = 'Smoker'
                AND price > 50
                AND price < 100
                """
	cursor.execute(view_query)
	print(mycursor.fetchall())

#Marketplace will start to return bad results eventually so need to remove those items for data integrity
def remove_irrelevant(cursor):
    clean_query = """
                DELETE 
                FROM items3 
                WHERE category = 'Smoker'
                AND title NOT LIKE '%smoker%'
                AND title NOT LIKE '%bbq%'  
                  """
    cursor.execute(clean_query)
    db.commit()

def update_data(cursor, old_val, new_val):
	update_query = 'UPDATE items2 SET price = %s WHERE price = %s'
	input_data = (old_val,new_val)
	cursor.execute(update_query, input_data)
	db.commit()

#Extracts single values into a list of int/str 
def get_single_data(cursor,query):
	cursor.execute(query)
	raw_rows = cursor.fetchall()
	list_data = [i[0] for i in raw_rows]
	price = [num for num in list_data if num is not None if num < 1000] #Need to remove None because it's not numeric and messes up graphing and math operations
	return(price)

#Extracts corresponding data into a list of tuples
def get_tuple_data(cursor, query):
	cursor.execute(query)
	rows = cursor.fetchall()
	raw_tuple = [data for data in rows]
	price_tuple = [tup for tup in raw_tuple if tup[1] is not None if tup[1] < 1000] #This crudely removes outliers, need a way which respects the different price ranges
	return(price_tuple) 

	#return pd.DataFrame(cursor.fetchall()) #This is one approach, but may be more effective to just plot straight from the output list

def get_price_info(data):
    data_array = np.array(data)
    lowest_price = np.min(data_array[np.nonzero(data_array)])
    average_price = np.mean(data)
    median_price = np.median(data)
    print('Lowest price: ', lowest_price, '\n\nAverage Price: ',average_price, '\n\n Median Price: ',median_price)

def scatter_plt (data):
	if isinstance(data[1], int): #If lets this accept data from single value or tuple source
		fig = plt.scatter(data, len(data)*[1])
	elif isinstance(data[1], tuple):
		fig = plt.scatter(*zip(*data)) #Splits columns of tuple into 2 lists
	plt.xticks(rotation = 45)
	plt.show()

#Creates a histogram of data, usually price, to effectively visualize the price range
def hist_plt (data):
	plt.hist(data,bins=len(set(data)), rwidth = 0.75)
	plt.xlabel('Price')
	plt.ylabel('Count')
	plt.show()


view_data(mycursor)
# remove_irrelevant(mycursor)
#update_data(mycursor,None,0)
#print(get_tuple_data(mycursor, title_price_query)
#get_price_info(get_single_data(mycursor, price_query))
#scatter_plt(get_single_data(mycursor, title_price_query))
#scatter_plt(get_tuple_data(mycursor, title_price_query))
#hist_plt(get_single_data(mycursor,price_query))
