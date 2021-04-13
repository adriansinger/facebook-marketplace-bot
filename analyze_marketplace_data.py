import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from price_comparison_tool import get_login_creds
import datetime

def main():
	full_creds = get_login_creds()
	sql_user = full_creds[2]
	sql_password = full_creds[3]

	db = mysql.connector.connect(
		host = 'localhost',
		user = sql_user,
		passwd = sql_password,
		database = 'facebook_marketplace_items'
		)

	#mycursor.execute('CREATE TABLE items4 (itemID int PRIMARY KEY AUTO_INCREMENT, urlID LONGTEXT UNIQUE, title LONGTEXT, price int UNSIGNED, description LONGTEXT, category VARCHAR(100), first_date_scraped DATETIME NOT NULL, recent_date_scraped DATETIME NOT NULL)') #Unsigned means it's always positive, the itemID could be the item URI

	raw_data = pd.read_sql_query("SELECT * FROM items3 WHERE category = 'Smoker'", db)
	print(raw_data.head())

main()