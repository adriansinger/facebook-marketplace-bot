import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


f = open(r'C:\Users\asing\Python\FB_Marketplace_Price\login.txt',"r")
lines = [line.strip() for line in f]
sql_user = lines[2]
sql_password = lines[3]
f.close()

db = mysql.connector.connect(
	host = 'localhost',
	user = sql_user,
	passwd = sql_password,
	database = 'facebook_marketplace_items'
	)

mycursor = db.cursor()


price_query = """
			  select price
			  from items3
			  """

title_price_query = """
					select itemID, price
					from items3
					"""

 

def view_data(cursor):
	view_query = 'SELECT title, price FROM items3 WHERE category = "Monitor"'
	cursor.execute(view_query)
	print(mycursor.fetchall())

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
	lowest_price = min(data)
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


#update_data(mycursor,None,0)
view_data(mycursor)
#print(get_tuple_data(mycursor, title_price_query)
#get_price_info(get_single_data(mycursor, price_query))
#scatter_plt(get_single_data(mycursor, title_price_query))
#scatter_plt(get_tuple_data(mycursor, title_price_query))
#hist_plt(get_single_data(mycursor,price_query))
