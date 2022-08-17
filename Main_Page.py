# Contents of ~/my_app/main_page.py
import streamlit as st

st.markdown("""
### NLB Bookmarked Books Aggregator!
#### Why this web app?

I love the Singapore NLB, and I think their app is great! However, I found their `Favorites` difficult to navigate. The `Favorites` is where we bookmark library books of our interest. Unfortunately, currently on the app, we are only able to look at our favorite books by per title level. This makes for a cumbersome user experience, because every time I am at a library, I have to check each book on their availability at a particular library. What I wanted is a view of my favorite books that are available by their library locations.

This web app is my attempt to address that problem. Previously, I had an approach where I scraped the NLB url links of my Favorites NLB books, and then scrape the availability information from those NLB links. This approach was slowly and prone to errors. 

Recently, I learned about the NLB open API, and managed to get access to it. Here, I am refactoring my original code to utilise the NLB APIs, and see if I can publish this as a proof-of-concept product.

#### How to use this web app?
1. Go to `Step 1 Get Yr Bks`
1. Key in your NLB username and password 
    1. *Note: We do not store any data*
1. Press `Extract data`
    1. *Note: Do not leave this page until the extraction is complete.* 
1. Once the extraction is down, press `Download csv`.
1. This downloads a csv file into your phone or laptop.
1. Note where the file is downloaded.
1. Go to `Step 2 Know Yr Bks`
1. Upload the downloaded file from `Step 1`.
1. Your bookmarked NLB books will show up as a table below.

### TO-DOs by me
1. ~Add login section~
1. ~Add better descriptions and prompts for Data Extraction Page~
1. Upload onto Streamlit Cloud
1. Add Google Analytics Tracker for user analytics
""")

