from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument(" --disable-gpu")
chrome_options.add_argument(" --disable-infobars")
chrome_options.add_argument(" -–disable-web-security")
chrome_options.add_argument("--no-sandbox") 

webdriver.Chrome(
    executable_path='chromedriver.exe', chrome_options=chrome_options)