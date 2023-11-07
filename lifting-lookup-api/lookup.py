from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lookup import LiftingCast

from concurrent.futures import ThreadPoolExecutor
import threading
import queue

import os

import concurrent.futures

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )
    driver.implicitly_wait(2)
    return driver


def fetch_lifters_from_meet(meet, driver_queue, all_lifters, lock):
    print(f"fetching lifters for {meet['name']}")
    try:
        print(f"{meet['name']} attempting to get driver from queue")
        with lock:
            driver = driver_queue.get(timeout=5)
        print(f"{meet['name']} successfuly got driver from queue")
    except queue.Empty:
        print(f"{meet['name']} could not get a driver from the queue")
    meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
    try:
        driver.get(meet_url)
        print(f"waiting for {meet['name']} to load")
        wait = WebDriverWait(driver, timeout=5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'meet-info-row')))
        print(f"{meet['name']} finished loading, getting names now")
        lifters = driver.find_elements(By.TAG_NAME, "a")
        result = []
        for lifter in lifters:
            lifter_id = lifter.get_attribute("href").split("/")[-1]
            result.append(
                {
                    "name": lifter.text,
                    "lifter_id": lifter_id,
                    "meet": meet["name"],
                    "meet_id": meet["meet_id"],
                }
            )
        print(f"fetched {len(result)} lifters for {meet["name"]}")
        with lock:
            all_lifters.extend(result)
            driver_queue.put(driver)
    except Exception as e:
        print(e)
    
liftingcast = LiftingCast()
liftingcast.fetch_meets()

number_of_drivers = 12
driver_queue = queue.Queue(number_of_drivers)
for d in range(number_of_drivers):
    driver_queue.put(get_driver())
all_lifters = []
lock = threading.Lock()

with concurrent.futures.ThreadPoolExecutor(number_of_drivers) as executor:
    for meet in liftingcast.meets:
        executor.submit(fetch_lifters_from_meet, meet, driver_queue, all_lifters, lock)

threads = []
with ThreadPoolExecutor(max_workers=number_of_drivers-1) as executor:
    for meet in liftingcast.meets:
        thread = executor.submit(fetch_lifters_from_meet, meet, all_lifters, lock)

while not driver_queue.empty():
    driver = driver_queue.get()
    driver.quit()

if os.path.exists('lifters.txt'):
    os.remove('lifters.txt')

errored_lifters = 0
with open('lifters.txt', 'w+') as f:
    for lifter in all_lifters:
        try:
            f.write(f"{lifter}\n")
        except:
            errored_lifters += 1
            print('unable to write lifter')
    
print(f'number of errored lifteres: {errored_lifters}')


