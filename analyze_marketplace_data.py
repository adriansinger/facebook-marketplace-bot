import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from price_comparison_tool import get_login_creds
import datetime

def price_stats(data):
	avg_price = data['price'].mean()
	median_price = data['price'].median()
	lowest_price = data[data['price'] > 0]['price'].min()

	print('Average price is: ', avg_price, '\nMedian price is: ', median_price, '\nLowest price is: ', lowest_price)

#Adding sold qualifier if most recent date scraped is less than today only works if running the scraper daily
def add_sold(data):
	to_datetime_data = datetime.datetime.strptime(data, '%Y-%m-%d') #Recent date scraped is in string format, need to revert to datetime to do comparison
	if to_datetime_data < datetime.datetime.now():
		return True
	else:
		return False

#Some list prices are invalid ex. 12345, 99999 and need to be ignored 
#Function expects single data item, to be applied to each row
def id_valid_price(data):
	invalid_values_list = ['0', '1', '123', '1234', '12345', '99999'] #Int are not iterable so need to cast to str
	if any(inval in str(data) for inval in invalid_values_list): 
		return 'Valid'
	else:
		return 'Invalid'


#MySQL is failing with frequent SQL reads, so going to write the db to a csv for testing purposes
def sql_to_csv(): 
	full_creds = get_login_creds()
	sql_user = full_creds[2]
	sql_password = full_creds[3]

	db = mysql.connector.connect(
		host = 'localhost',
		user = sql_user,
		passwd = sql_password,
		database = 'facebook_marketplace_items'
		)

	raw_data_sql = pd.read_sql_query("SELECT * FROM items3 WHERE category = 'Smoker'", db)
	db.close()

	raw_data_sql.to_csv('most_recent_fb_data.csv')

def main():
	#sql_to_csv()

	raw_data = pd.read_csv('most_recent_fb_data.csv')
	raw_data['is_valid_price'] = raw_data['price'].apply(id_valid_price)
	print(raw_data.loc[raw_data['is_valid_price']=='Invalid'])

main()