import awswrangler as wr
import boto3
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from concurrent.futures import ThreadPoolExecutor

liftingcast_home = "https://liftingcast.com/"

number_of_worker_threads = 3


def split_list_into_chunks(l, nchunks):
    for i in range(nchunks):
        yield l[i::nchunks]


class LiftingCast:
    def __init__(self):
        self.meets = []
        self.failed_meets = []
        self.lifters = []

    def get_webdirver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("enable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        # service = webdriver.ChromeService("/usr/bin/chromedriver")
        # driver = webdriver.Chrome(options=options, service=service)
        driver = webdriver.Chrome(options=options)

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

    def fetch_lifters_from_meet(self, meet, driver):
        meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
        try:
            driver.get(meet_url)
            wait = WebDriverWait(driver, timeout=15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "meet-info-row")))
        except Exception as e:
            print("EXCEPTION WHILE WAITING FOR " + meet["name"] + " TO LOAD")
            print(e)
            self.failed_meets.append(meet)
            return []

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
                    "meet_date": meet["date"],
                }
            )
        print(f"fetched {len(result)} lifters for {meet['name']}")
        return result

    def process_meets(self, meets):
        driver = self.get_webdirver()
        result_collector = []
        for meet in meets:
            result_collector.extend(self.fetch_lifters_from_meet(meet, driver))
        driver.quit()

        return result_collector

    def begin_threaded_search(self, meets):
        meet_buckets = split_list_into_chunks(meets, number_of_worker_threads)

        with ThreadPoolExecutor(number_of_worker_threads) as executor:
            futures = [
                executor.submit(self.process_meets, bucket) for bucket in meet_buckets
            ]
        result = [f.result() for f in futures]
        return [lifter for meet in result for lifter in meet]

    def fetch_lifters(self):
        result = self.begin_threaded_search(self.meets)
        print("initial search done. " + str(len(self.failed_meets)) + " meets failed.")
        while len(self.failed_meets):
            print(
                "starting passthrough of failed meets. "
                + str(len(self.failed_meets))
                + " meets need to be processed."
            )
            meets_to_process = []
            for meet in self.failed_meets:
                meets_to_process.append(meet)
            self.failed_meets = []
            successful_meets = self.begin_threaded_search(meets_to_process)
            print("failed_meet iteration finished.")
            result.extend(successful_meets)
        self.lifters = result


def handler(event=None, context=None):
    # set up aws stuff
    print("Initializing environment")
    load_dotenv()
    region = os.environ.get("AWS_REGION")
    lifter_table_name = os.environ.get("AWS_DYNAMO_LIFTER_TABLE_NAME")
    lifter_update_table_name = os.environ.get("AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME")
    boto3.setup_default_session(region_name=region)

    # fetch lifters
    print("Initializing LiftingCast")
    L = LiftingCast()
    print("Fetching meets")
    L.fetch_meets()
    print("Fetching lifters")
    L.fetch_lifters()

    scraped_lifters = pd.DataFrame(L.lifters)

    # lifters that we are currently storing
    print("Fetching lifters from dynamo")
    stored_lifters = wr.dynamodb.read_items(
        table_name=lifter_table_name, allow_full_scan=True
    )

    # create two dataframes for each action we need to do
    lifters_to_delete = pd.DataFrame()
    lifters_to_insert = pd.DataFrame()
    if "lifter_id" in scraped_lifters.columns and "lifter_id" in stored_lifters.columns:
        lifters_to_delete = stored_lifters[
            ~stored_lifters.lifter_id.isin(scraped_lifters.lifter_id)
        ]
        lifters_to_insert = scraped_lifters[
            ~scraped_lifters.lifter_id.isin(stored_lifters.lifter_id)
        ]

    # delete any lifters we are currenlty storing that we did not scrape
    print(f"{len(lifters_to_delete.index)} lifters to delete")
    if "lifter_id" in lifters_to_delete.columns:
        wr.dynamodb.delete_items(
            items=lifters_to_delete.to_dict("records"), table_name=lifter_table_name
        )

    # insert any lifters we scraped that we are currently not storing
    print(f"{len(lifters_to_insert.index)} lifters to insert")
    if "lifter_id" in lifters_to_insert.columns:
        wr.dynamodb.put_df(df=lifters_to_insert, table_name=lifter_table_name)

    # make note of the update we just did
    print(f"recording update datetime")
    wr.dynamodb.put_items(
        items=[
            {
                "update_datetime": str(datetime.now()),
                "insertion_count": len(lifters_to_insert.index),
                "deletion_count": len(lifters_to_delete.index),
            }
        ],
        table_name=lifter_update_table_name,
    )

    # all done
    print("DONE")
    return "Success"


handler()
