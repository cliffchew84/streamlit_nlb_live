import os
import re
import time
import math
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

driver = webdriver.Chrome(options=options)
log_in_nlb(driver, st.secrets['nlb_login_account'], st.secrets['nlb_login_pw'])

url_link = "https://www.nlb.gov.sg/mylibrary/Bookmarks"
driver.get(url_link)
time.sleep(5)
soup = bs(driver.page_source, 'html5lib')

max_records = float(soup.find_all("div", text=re.compile("Showing"))[0].text.split(" ")[-2])
range_list = range(1, int(math.ceil(max_records / 20)) + 1)

# To indicate when the NEXT button is at
counter = range_list[-1] + 2
st.write(counter)
