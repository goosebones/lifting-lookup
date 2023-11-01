# %%
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


load_dotenv()

# %%
liftingcast_meet_id = "myg93vz44cq3"
liftingcast_platform_id = "pitzxifyqn2c"

url = f"https://liftingcast.com/meets/{liftingcast_meet_id}/platforms/{liftingcast_platform_id}/display"

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(
    options=options, service=ChromeService(ChromeDriverManager().install())
)

driver.get(url)


# %%
def get_running_order():
    order_tablefirst_col = driver.find_elements(By.CLASS_NAME, "first-column")
    running_order = []
    for selenium_webelement in order_tablefirst_col:
        classes = selenium_webelement.get_attribute("class").split()
        if "table-header" in classes:
            continue
        elif "table-cell-title" in classes:
            running_order.append(
                {"type": "section_divider", "name": selenium_webelement.text}
            )
        else:
            running_order.append({"type": "lifter", "name": selenium_webelement.text})
    return running_order
