from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

from util import split_list_into_chunks

liftingcast_home = "https://liftingcast.com/"
number_of_worker_threads = 3


class LiftingCastException(Exception):
    pass


class LiftingCast:
    def __init__(self):
        pass

    def get_webdirver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("enable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
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
        driver.quit()
        return meets

    def fetch_lifters_from_meet(self, meet, driver):
        meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
        try:
            driver.get(meet_url)
            wait = WebDriverWait(driver, timeout=15)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "meet-info-row")))
        except Exception as e:
            print("EXCEPTION WHILE WAITING FOR " + meet["name"] + " TO LOAD")
            print(e)
            raise LiftingCastException

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
        failed_meets = []
        for meet in meets:
            try:
                lifters = self.fetch_lifters_from_meet(meet, driver)
                result_collector.extend(lifters)
            except LiftingCastException:
                failed_meets.append(meet)
        driver.quit()

        return result_collector, failed_meets

    def begin_threaded_meets_search(self, meets):
        meet_buckets = split_list_into_chunks(meets, number_of_worker_threads)

        with ThreadPoolExecutor(number_of_worker_threads) as executor:
            futures = [
                executor.submit(self.process_meets, bucket) for bucket in meet_buckets
            ]
        result = [f.result() for f in futures]
        lifters = []
        failed_meets = []
        for res in result:
            res_lifters, res_failed_meets = res
            lifters.extend(res_lifters)
            failed_meets.extend(res_failed_meets)
        return lifters, failed_meets

    def fetch_lifters(self, meets):
        result_collector = []
        meets_to_process = meets
        print("begin fetch_lifters")
        while len(meets_to_process):
            print(f"begin fetch_lifters iteration - {str(len(meets_to_process))} meets")
            lifters, failed_meets = self.begin_threaded_meets_search(meets_to_process)
            result_collector.extend(lifters)
            meets_to_process = failed_meets
            print(f"fetch_lifters iteration finished. Failed: {str(len(failed_meets))}")
        print("end fetch_lifters")
        return result_collector
