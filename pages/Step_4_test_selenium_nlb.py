import os
import re
import time
import math
import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")


account_name = st.secrets['nlb_login_account']
password = st.secrets['nlb_login_pw']


def log_in_nlb(browser, account_name: str, password: str):
    """ Logins into the NLB app, and returns selenium browser object
    """

    # Go login page
    browser.get('https://cassamv2.nlb.gov.sg/cas/login')
    time.sleep(1)
    
    account_info = [account_name, password]
    tag_info = ["""//*[@id="username"]""", """//*[@id="password"]"""]
    
    for info, tag in zip(account_info, tag_info):
        browser.find_element("xpath", tag).send_keys("{}".format(info))
        time.sleep(1)
    
    # Click login
    browser.find_element("xpath", """//*[@id="fm1"]/section/input[4]""").click()
    return browser


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

## Actualy scraping
driver = webdriver.Chrome(options=options)
log_in_nlb(driver, account_name, password)

url_link = "https://www.nlb.gov.sg/mylibrary/Bookmarks"
driver.get(url_link)
time.sleep(10)
soup = bs(driver.page_source)

max_records = float(soup.find_all("div", text=re.compile("Showing"))[0].text.split(" ")[-2])
range_list = range(1, int(math.ceil(max_records / 20)) + 1)

# To indicate when the NEXT button is at
counter = range_list[-1] + 2
st.write(counter)

# Scraping the pages
book_urls_dict = dict()
book_urls_dict[0] = list(set(get_book_urls_on_page(soup)))
next_button = f'//*[@id="bookmark-folder-content"]/nav/ul/li[{counter}]/a'

for i in range(1,counter-2):
    try:
        print(i)
        time.sleep(10)
        driver.find_element('xpath', next_button).click()
        soup = bs(browser.page_source, 'html5lib')
        book_urls_dict[i] = list(set(get_book_urls_on_page(soup)))
        time.sleep(2)
    except:
        print("end of page")

st.write(book_urls_dict)