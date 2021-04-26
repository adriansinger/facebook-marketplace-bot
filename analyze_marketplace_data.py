import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from price_comparison_tool import get_login_creds
from datetime import datetime, date, timedelta

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

#Adding sold qualifier if most recent date scraped is less than today only works if running the scraper daily
def add_sold(data, curr_scrape_date):
	to_datetime_data = datetime.strptime(data, '%Y-%m-%d') #Recent date scraped is in string format, need to revert to datetime to do comparison
	if to_datetime_data < curr_scrape_date:
		return True
	else:
		return False

#Some list prices are invalid ex. 12345, 99999 and need to be ignored 
#Function expects single data item, to be applied to each row
def id_valid_price(data):
	invalid_values_list = ['0', '1', '123', '1234', '12345', '99999'] #Int are not iterable so need to cast to str
	if str(data) in invalid_values_list: 
		return 'Invalid'
	else:
		return 'Valid'

#Function adds a column of int values calculating the number of days an item took to sell
def add_time_to_sell(first_date, recent_date):
	delta = datetime.strptime(recent_date, '%Y-%m-%d') - datetime.strptime(first_date, '%Y-%m-%d')
	return delta.days

def price_stats(data):
	avg_price = round(data['price'].mean(),2)
	median_price = data['price'].median()
	lowest_price = data[data['price'] > 0]['price'].min()
	avg_time_to_sell = round(data['days_to_sell'].mean(),1)
	#avg_time_to_sell = sum(data['days_to_sell'],timedelta(0))/len(data['days_to_sell']) #Need to start the sum with a timedelta object otherwise defaults to int

	print('Average price is: ', avg_price, '\nMedian price is: ', median_price, '\nLowest price is: ', lowest_price, '\nAverage time to sell is: ', avg_time_to_sell)

def get_optimal_price(data, start_range, end_range):
	dt_df = pd.to_datetime(data['recent_date_scraped']) 	
	data_in_range = data[(dt_df > start_range) & (dt_df < end_range)] #Slice for dataset within the date range
	data_range_nonzero = data_in_range[data_in_range['price'] > 1] #Remove unrealistic values here, could replace with a historical average price value
	return data_range_nonzero['price'].min()

def main():
	#sql_to_csv()
	raw_data = pd.read_csv('most_recent_fb_data.csv')

	curr_scrape_date = datetime.strptime(max(raw_data['recent_date_scraped']), '%Y-%m-%d')
	raw_data['is_sold'] = (raw_data['recent_date_scraped'].apply(add_sold, args=(curr_scrape_date,)))
	raw_data['is_valid_price'] = raw_data['price'].apply(id_valid_price)
	raw_data['days_to_sell'] = raw_data.apply(lambda x: add_time_to_sell(x['first_date_scraped'], x['recent_date_scraped']), axis=1)

	print(get_optimal_price(raw_data, datetime.strptime('2021-03-01', '%Y-%m-%d'), datetime.strptime('2021-03-31', '%Y-%m-%d')))
	#print(raw_data.loc[raw_data['is_sold']==True])

main()