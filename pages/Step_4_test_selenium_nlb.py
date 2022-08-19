import os
import re
import math
import time
import numpy as np
import pandas as pd
import streamlit as st
from zeep import Client, helpers

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from nlb_api_fun import *

API = st.secrets['nlb_api_keys']
account_name = st.secrets['nlb_login_account']
password = st.secrets['nlb_login_pw']

# Web scraping parameters
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument('''--user-agent="Mozilla/5.0 (Windows NT 6.1; 
WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"''')


def log_in_nlb(driver, account_name: str, password: str):
    """ Logins into the NLB app, and returns selenium driver object
    """

    # Go login page
    driver.get('https://cassamv2.nlb.gov.sg/cas/login')
    time.sleep(1)
    
    account_info = [account_name, password]
    tag_info = ["""//*[@id="username"]""", """//*[@id="password"]"""]
    
    for info, tag in zip(account_info, tag_info):
        driver.find_element("xpath", tag).send_keys("{}".format(info))
        time.sleep(1)
    
    # Click login
    driver.find_element("xpath", """//*[@id="fm1"]/section/input[4]""").click()
    return driver


def get_book_urls_on_page(soup):
    """ Getting book urls from page for NLB project 
    Args: BeautifulSoup Object
    Returns: List of book urls (list)
    
    """

    book_urls_list = list()
    for a in soup.find_all('a', href=True):
        if "catalogue" in a['href']:
            book_urls_list.append(a['href'])
    return book_urls_list

## Apply scraping
driver = webdriver.Chrome(options=options)
log_in_nlb(driver, account_name, password)

url_link = "https://www.nlb.gov.sg/mylibrary/Bookmarks"
driver.get(url_link)
time.sleep(5)
soup = bs(driver.page_source)

max_records = float(soup.find_all("div", text=re.compile("Showing"))[0].text.split(" ")[-2])
range_list = range(1, int(math.ceil(max_records / 20)) + 1)

# To indicate when the NEXT button is at
counter = range_list[-1] + 2
st.markdown(f"{range_list}")

# Scraping the pages
book_urls_dict = dict()
book_urls_dict[0] = list(set(get_book_urls_on_page(soup)))
next_button = f'//*[@id="bookmark-folder-content"]/nav/ul/li[{counter}]/a'

# Convoluted way of extracting data
for i in range(1,counter-2):
    try:
        time.sleep(8)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, next_button)))
        webdriver.ActionChains(driver).move_to_element(element ).click(element ).perform()
        time.sleep(8)
        soup = bs(driver.page_source)
        book_urls_dict[i] = list(set(get_book_urls_on_page(soup)))
    
    except:
        print(f'{i} error')
        time.sleep(8)
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, next_button)))
        webdriver.ActionChains(driver).move_to_element(element ).click(element ).perform()
        time.sleep(8)
        
        soup = bs(driver.page_source)
        book_urls_dict[i] = list(set(get_book_urls_on_page(soup)))

# Produce out all my urls
st.write(book_urls_dict)

all_book_url_lists = list()
for i in range(0, len(book_urls_dict)):
    all_book_url_lists = all_book_url_lists + book_urls_dict[i]

unique_books = set(all_book_url_lists)
list_of_book_bids = [re.findall(r'\d+', i)[-1] for i in list(unique_books)]
st.write(f"No of unique books: {len(list_of_book_bids)}")


st.markdown("### Combining different datasets")
df = pd.DataFrame()
bid_w_issues = list()

my_bar = st.progress(0)

for i, bid_no in enumerate(list_of_book_bids):
    # try:
    avail_book_obj = make_get_avail_api_call(API, bid_no)
    avail_book_df = df_get_avail_data(bid_no, avail_book_obj)

    title_detail_obj = make_get_title_details_api_call(bid_no)
    title_detail_df = df_get_title_data(title_detail_obj)
    
    final_book_df = final_book_avail_df(avail_book_df, title_detail_df)
    final_book_df['url'] = return_needed_url(API, bid_no)
    
    df = df.append(final_book_df)
    my_bar.progress(i/max_books)
    
    # except:
    #     bid_w_issues.append(bid_no)
    #     my_bar.progress(i/max_books)

df = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download your bookmarked books",
    data=df,
    file_name="bookmarked_books.csv",
    mime="text/csv"
)