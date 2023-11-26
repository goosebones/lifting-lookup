from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from concurrent.futures import ThreadPoolExecutor
import threading
import queue

import os
import json


liftingcast_home = "https://liftingcast.com/"
number_of_drivers_for_lifter_fetch = 12
lifters_output_filename = 'lifters.json'


class LiftingCast:
    def __init__(self):
        self.meets = []
        self.lifters = []

    def get_webdirver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(
            options=options, service=ChromeService(ChromeDriverManager().install())
        )
        driver.implicitly_wait(2)
        return driver

    def fetch_meets(self):
        driver = self.get_webdirver()
        driver.get(liftingcast_home)
        tables = driver.find_elements(By.CLASS_NAME, "table")
        upcoming_meets = None
        recent_meets = None
        for table in tables:
            head = table.find_element(By.XPATH, ("./thead"))
            if "Upcoming Meets" in head.text:
                upcoming_meets = table
            elif "Recent Meets" in head.text:
                recent_meets = table

        meets = []
        for meet_table in [upcoming_meets, recent_meets]:
            rows = meet_table.find_elements(By.XPATH, ("./tbody/tr"))
            for row in rows:
                [name, date] = row.find_elements(By.XPATH, ("./td"))
                meet_id = (
                    name.find_element(By.XPATH, ("./a"))
                    .get_attribute("href")
                    .split("/")[4]
                )
                meets.append({"name": name.text, "date": date.text, "meet_id": meet_id})
        self.meets = meets
        driver.quit()

    def fetch_lifters(self):
        def fetch_lifters_from_meet(meet, driver_queue, result_list, lock):
            try:
                with lock:
                    driver = driver_queue.get(timeout=5)
            except queue.empty:
                print(f"{meet['name']} could not get a driver from the queue")
            
            meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
            driver.get(meet_url)
            wait = WebDriverWait(driver, timeout=5)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'meet-info-row')))

            lifters = driver.find_elements(By.TAG_NAME, "a")
            result = []
            for lifter in lifters:
                lifter_id = lifter.get_attribute("href").split("/")[-1]
                result.append(
                    {
                        "lifter_name": lifter.text,
                        "lifter_id": lifter_id,
                        "meet_name": meet["name"],
                        "meet_id": meet["meet_id"],
                        "meet_date": meet["date"]
                    }
                )
            print(f"fetched {len(result)} lifters for {meet["name"]}")

            with lock:
                result_list.extend(result)
                driver_queue.put(driver)

        number_of_drivers = number_of_drivers_for_lifter_fetch
        driver_queue = queue.Queue(number_of_drivers)
        for d in range(number_of_drivers):
            driver_queue.put(self.get_webdirver())
        all_lifters = []
        lock = threading.Lock()
        self.fetch_meets()
        with ThreadPoolExecutor(number_of_drivers) as executor:
            for meet in self.meets:
                executor.submit(fetch_lifters_from_meet, meet, driver_queue, all_lifters, lock)

        for d in driver_queue.queue:
            d.quit()

        self.lifters = all_lifters

        lifter_file = os.path.join(os.path.dirname(__file__), lifters_output_filename)
        if os.path.exists(lifter_file):
            os.remove(lifter_file)

        with open(lifter_file, 'w') as f:
            f.write(json.dumps(all_lifters))
