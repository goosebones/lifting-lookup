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
from tempfile import mkdtemp

liftingcast_home = "https://liftingcast.com/"

number_of_worker_threads = 3


class LiftingCast:
    def __init__(self):
        self.meets = []
        self.lifters = []
        self.driver = self.get_webdirver()

    def get_webdirver(self):
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService("/opt/chromedriver")
        options.binary_location = "/opt/chrome/chrome"

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")

        chrome = webdriver.Chrome(options=options, service=service)
        chrome.implicitly_wait(2)
        return chrome

    def fetch_meets(self):
        self.driver.get(liftingcast_home)
        tables = self.driver.find_elements(By.CLASS_NAME, "table")
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

    def fetch_lifters(self):
        def fetch_lifters_from_meet(meet, driver):
            meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
            try:
                driver.get(meet_url)
                wait = WebDriverWait(driver, timeout=15)
                wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "meet-info-row"))
                )
            except Exception as e:
                print("EXCEPTION WHILE WAITING FOR " + meet["name"] + " TO LOAD")
                print(e)

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

        def process_meets(meets):
            driver = self.get_webdirver()
            result_collector = []
            for meet in meets:
                result_collector.extend(fetch_lifters_from_meet(meet, driver))
            return result_collector

        def split_list_into_chunks(l, nchunks):
            for i in range(nchunks):
                yield l[i::nchunks]

        meet_buckets = split_list_into_chunks(self.meets, number_of_worker_threads)

        with ThreadPoolExecutor(number_of_worker_threads) as executor:
            futures = [
                executor.submit(process_meets, bucket) for bucket in meet_buckets
            ]
        result = [f.result() for f in futures]
        self.lifters = [lifter for meet in result for lifter in meet]


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
