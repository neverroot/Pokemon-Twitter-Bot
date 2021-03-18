# Python file that will deal with Browser control

import selenium as selenium
from selenium import webdriver
from bs4 import BeautifulSoup


# browser control
def control_browser():
    browser = webdriver.Chrome(executable_path="/home/rusty/opt/chromedriver")
    browser.get("https://www.pokemoncenter.com/search/plushie")
    html = browser.page_source
    soup = BeautifulSoup(html)
    print(html)
