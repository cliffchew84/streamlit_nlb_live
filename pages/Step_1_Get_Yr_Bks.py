import os
import sys
import numpy as np
import pandas as pd
import streamlit as st

from bs4 import BeautifulSoup as bs
from zeep import Client, helpers
import rpa as r
import math
import time
import re

from nlb_api_fun import *

pd.set_option('display.max_colwidth',None)

## Methods
def rpa_nlb_login(account_name, pw):
    
    r.init(headless_mode=True)
    
    r.url("https://cassamv2.nlb.gov.sg/cas/login")
    r.type('//*[@id="username"]', f'{account_name}')
    r.type('//*[@id="password"]', f'{password}')

    r.click("""//*[@id="fm1"]/section/input[4]""")

    return r

############ Either use secrets from Streamlit or from my own system ############
if sys.platform == "darwin":
    API = os.environ['nlb_api_keys']

else:
    API = st.secrets['nlb_api_keys']


############ Filter to get the necessary ############
# st.set_page_config(layout="wide")

with st.form("my_form"):
    account_name = st.text_input("NLB User Name")
    password = st.text_input("NLB Password", type='password')

    submitted = st.form_submit_button("Extract Data")

st.markdown(""" 
    ##### Things to Note:
    1. ***We respect your privacy! We do not store your data!***
    1. Do not click on the other parts of this web app until the extraction is complete. If not, the extraction will stop and you have to restart your extraction. Unfortunately, the web app is still a bit slow. You can look at other tabs of your browser. 
    1. Once the extraction is complete, a `Download CSV` button will pop up for you to download the data into your laptop or phone.
    1. Upload this data into Step 2 to review the locations of the books available.
""")

try:
    if submitted:
        st.markdown("""---""")
        # NLB login
        with st.spinner(text="Logging into NLB..."):
            # account_name = os.environ['nlb_login_account']
            # password = os.environ['nlb_login_pw']

            r = rpa_nlb_login(account_name, password)

        # NLB bookmark scraping
        with st.spinner(text="Going thru bookmarked pages..."):
            r.url("https://www.nlb.gov.sg/mylibrary/Bookmarks")
            time.sleep(5)

            soup = bs(r.read('page'), 'html5')
            max_records = float(
                soup.find_all(
                    "div", 
                    text=re.compile("Showing")
                )[0].text.split(" ")[-2])

            range_list = range(1, int(math.ceil(max_records / 20)) + 1)

            # To indicate when the NEXT button is at
            counter = range_list[-1] + 2


        with st.spinner(text="Getting books..."):
            book_urls_dict = dict()
            soup = bs(r.read('page'), 'html5')
            book_urls_dict[0] = list(set(get_book_urls_on_page(soup)))

            for i in range(1,counter+1):
                time.sleep(2)
                click_thru_pages = f'//*[@id="bookmark-folder-content"]/nav/ul/li[{counter}]/a'
                r.click(click_thru_pages)
                time.sleep(2)
                soup = bs(r.read('page'), 'html5')
                book_urls_dict[i] = list(set(get_book_urls_on_page(soup)))

            r.close()

        # List of unique books
        all_book_url_lists = list()
        for i in range(0, len(book_urls_dict)):
            all_book_url_lists = all_book_url_lists + book_urls_dict[i]

        unique_books = set(all_book_url_lists)
        list_of_book_bids = [re.findall(r'\d+', i)[-1] for i in list(unique_books)]
        st.markdown(f"No of unique books: {len(list_of_book_bids)}")


        # NLB API Calls
        df = pd.DataFrame()
        bid_w_issues = list()

        my_bar = st.progress(0)
        max_books = len(list_of_book_bids)

        for i, bid_no in enumerate(list_of_book_bids):
            try:
                avail_book_obj = make_get_avail_api_call(bid_no)
                avail_book_df = df_get_avail_data(bid_no, avail_book_obj)

                title_detail_obj = make_get_title_details_api_call(bid_no)
                title_detail_df = df_get_title_data(title_detail_obj)
                
                final_book_df = final_book_avail_df(avail_book_df, title_detail_df)
                final_book_df['url'] = return_needed_url(bid_no)
                
                df = df.append(final_book_df)
                my_bar.progress(i/max_books)
            
            except:
                bid_w_issues.append(bid_no)
                my_bar.progress(i/max_books)
        
        df = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download your bookmarked books",
            data=df,
            file_name="bookmarked_books.csv",
            mime="text/csv"
        )

except:
    st.markdown("""
        <span style="color:red">
            ***There is an issue with your account name or password.
            Please try again.***
        </span>
        """, unsafe_allow_html=True)