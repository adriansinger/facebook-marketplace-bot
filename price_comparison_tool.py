##Login to facebook and scrape marketplace
import MySQLdb
import mysql.connector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta, date
from sys import exit
import time

#Function needed to extract login credentials
def get_login_creds():
    f = open(r'C:\Users\asing\Python\FB_Marketplace_Price\login.txt',"r")
    lines = [line.strip() for line in f]
    fb_user = lines[0]
    fb_password = lines[1]
    sql_user = lines[2]
    sql_password = lines[3]
    f.close()

    return fb_user,fb_password, sql_user, sql_password


class facebookApp():
    def __init__(self, fb_user, fb_password, sql_user, sql_password):
        options = Options()
        options.headless = True #Prevents a visible chrome window from opening
        self.email = fb_user
        self.password = fb_password
        self.driver = webdriver.Firefox(options=options, executable_path=r"C:\Users\asing\Python\geckodriver") #Need to include executable path
        self.main_url = 'https://www.facebook.com/'
        self.used_item_links = [] #List for holding the links to each item in search screen
        self.driver.get(self.main_url)
        self.db = mysql.connector.connect(host='localhost',user=sql_user,passwd=sql_password, database='facebook_marketplace_items')
        time.sleep(5)

    #Creates table for storing scraped data
    def create_table(self):
        mycursor = self.db.cursor()
        mycursor.execute('CREATE TABLE items4 (itemID int PRIMARY KEY AUTO_INCREMENT, urlID LONGTEXT UNIQUE, title LONGTEXT, price int UNSIGNED, description LONGTEXT, category VARCHAR(100), first_date_scraped DATETIME NOT NULL, recent_date_scraped DATETIME NOT NULL)') #Unsigned means it's always positive, the itemID could be the item URI

    def login(self):
        try: 
            email_input = self.driver.find_element_by_id('email')
            email_input.send_keys(self.email)
            time.sleep(0.6)
            pw_input = self.driver.find_element_by_id('pass')
            pw_input.send_keys(self.password)
            time.sleep(0.4)
            login_button = self.driver.find_element_by_name('login')
            login_button.click()
            print('Login successful')
            time.sleep(3)
        
            
        except Exception as e:
            print('Login unsuccessful:', str(e))
            self.driver.quit()
            exit()
            
    def open_mktplace(self):
        try:
            marketplace_btn = self.driver.find_element_by_xpath('//span[contains(text(), "Marketplace")]') #Checks the text of all spans for any instance of marketplace
            marketplace_btn.click()
            print('Marketplace opened successfully')
            time.sleep(4)  
        except Exception as e:
            print('Unable to find marketplace button:', str(e))
            #self.driver.quit()
            exit()

    def search_item(self,item_name, location_name):
        try:
            search_bar = self.driver.find_element_by_xpath('//input[@placeholder="Search Marketplace"]') #Locates the marketplace search bar
            search_bar.send_keys(item_name)
            search_bar.send_keys(Keys.RETURN)
            print('Search successful')
            time.sleep(4)
        except:
            print('Unable to find marketplace search bar')
            self.driver.quit()
            exit()

        #Need to change location to within 10 km and sort by Listed Date    
        #Need to set distance and sorting here before scrolling because this resets the page
        #Facebook changed their layout so this will need to be fixed
        # location_box = self.driver.find_element_by_xpath('//span[@producttag="marketplace"]') #Use location select box as closest easily searchable field to location distance and sort by
        # ActionChains(self.driver).click(location_box).send_keys(location_name).send_keys(Keys.RETURN).perform()
        # ActionChains(self.driver).click(location_box).send_keys(Keys.TAB).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.RETURN).perform() #Manually get to within 10 km search because can't find the dropdown options in insepct element
        #ActionChains(self.driver).click(location_box).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys .DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.DOWN).send_keys(Keys.RETURN).perform() #Manually get to Date listed: Newest first

    def scrape_item_links(self):

        #Used to scroll down page in order to load more items, otherwise stale element error
        #To speed up the scrape, try doing while len(url_list) < 100 instead of just constantly running for loops
        for i in range(500): 
            try:
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(1.3)
            except Exception:
                pass
        
        print('Page scrolled')
        full_item_list = self.driver.find_elements_by_xpath('//a[contains(@class, "oajrlxb2")]') #Returns a list with location of all items links

        #Loops through each item from the location list and returns the unique portion of the URL 
        for item in full_item_list:
            try:
                if item.get_attribute('href').startswith('/marketplace/item', 24): #Page uses many href tags, this specifies only the item links
                    self.used_item_links.append(item.get_attribute('href'))
            except StaleElementReferenceException:
                self.used_item_links.append(None)
            
        return self.used_item_links

    def scrape_item_info(self,used_item_links,category):
        mycursor = self.db.cursor()

        #This loops through every item URL and retrives the desired data for that item
        counter = 1
        for url in used_item_links: 
            self.driver.get(url)
            time.sleep(10)

            try:
                price_raw = self.driver.find_element_by_xpath('//div[contains(@class, "dati1w0a qt6c0cv9 hv4rvrfc discj3wi")]/div[2]/div/span[1]').text #Locates the price element tag and extracts the text
                price_raw1 = price_raw.replace(',','').replace('C','') #For reduced prices in canadian dollars, a C will prepend the second $, need to remove it to match int format 
                
                if '·' in price_raw1: #Some titles say · In Stock, need to remove for int format
                    price_raw2, instock = price_raw1.split('·') 
                else:
                    price_raw2 = price_raw1

                if price_raw2.count('$') == 2: #if the price is reduced, both prices will be scraped with two $ characters and the reduced value appearing first
                    blank,price_str,orig_price = price_raw2.split('$') 
                    price = int(price_str) #Price was passing as a string, db expects int for price
                else:
                    price_str = price_raw2.replace('$','')
                    price = int(price_str)
            except Exception:
                print('\nPrice failed\n')
                price = 0 #Don't use None, it causes issues since it's not an int

            #The html xpath for title is used multiple times so always want to skip the first item scraped
            title_html = []
            title_html = self.driver.find_elements_by_xpath('//span[contains(@class,"iv3no6db o0t2es00 f530mmz5 hnhda86s")]')
            title = title_html[1].text

            try:
                description = self.driver.find_element_by_xpath('//div[contains(@class,"ii04i59q ")]/div/span').text
            except:
                description = ""
            
            urlId = url.split('/item/')[1]
            scraped_date = date.today() #Using a datetime object that does not include time

          
            #print('URL_ID:',urlId,'\nTitle:',title, '\nPrice:',price,'\nDescription:',description,'\nDate_Scraped:',scraped_date, '\nCategory:',category, '\n')
            
            insertQuery = """
                            INSERT INTO items3 (urlID, title, price, description, first_date_scraped, recent_date_scraped, category) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s) 
                            ON DUPLICATE KEY UPDATE recent_date_scraped = VALUES(recent_date_scraped) #This stops duplicates items and tracks when an item was last scraped, assume sold when it no longer appears
                          """
     
            insertValues = (urlId, title, price, description, scraped_date, scraped_date, category)

            try:
                mycursor.execute(insertQuery,insertValues)
                self.db.commit()
            except MySQLdb.Error as err: #If you get an error it will continue instead of stopping
                print('\nError:',err, '\n\n')
                continue #Need to validate that this works because I fixed the table directly rather than this because it was easier in this situation

            print('Completed scraping item:',counter,'/',len(used_item_links)) #This will act as a progress bar
            counter = counter + 1

        viewquery = 'SELECT * FROM items3' #Change query depending on the output data you want to view
        mycursor.execute(viewquery)
        print(mycursor.fetchall())



        self.driver.quit()

                
if __name__ == '__main__':
    start_time = time.monotonic()
    fb_app = facebookApp(*get_login_creds())
    fb_app.login()
    fb_app.open_mktplace()
    fb_app.search_item(item_name='smoker',location_name='Toronto')
    used_item_links = fb_app.scrape_item_links()
    fb_app.scrape_item_info(used_item_links,category='smoker')
    end_time = time.monotonic()
    print('Runtime: ', timedelta(seconds=end_time - start_time))
