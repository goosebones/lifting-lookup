from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from tqdm import tqdm

liftingcast_home = "https://liftingcast.com/"


class LiftingCast:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(
            options=options, service=ChromeService(ChromeDriverManager().install())
        )
        driver.implicitly_wait(2)
        driver.get(liftingcast_home)
        self.driver = driver
        self.meets = []
        self.lifters = []

    def fetch_meets(self):
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
        for meet in tqdm(self.meets):
            meet["Lifters"] = []
            meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
            self.driver.get(meet_url)
            lifters = self.driver.find_elements(By.TAG_NAME, "a")
            for lifter in lifters:
                lifter_id = lifter.get_attribute("href").split("/")[-1]
                meet["Lifters"].append(
                    {
                        "name": lifter.text,
                        "lifter_id": lifter_id,
                        "meet": meet["name"],
                        "meet_id": meet["meet_id"],
                    }
                )

    def fetch_lifter_details(self):
        for meet in tqdm(self.meets):
            for lifter in meet["Lifters"]:
                meet_lifter_url = f"https://liftingcast.com/meets/{meet['meet_id']}/lifter/{lifter['lifter_id']}/info"
                self.driver.get(meet_lifter_url)
                informations = self.driver.find_elements(By.CLASS_NAME, "info-row")
                for info in informations:
                    label = info.find_element(By.TAG_NAME, "label").text.replace(
                        ":", ""
                    )
                    value = info.find_element(By.TAG_NAME, "div").text
                    lifter[label] = value

    def get_lifters(self):
        return [meet["Lifters"] for meet in self.meets]


from multiprocessing import Pool


def fetch_lifters_from_meet(meet):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )
    driver.implicitly_wait(2)
    meet_url = f"https://liftingcast.com/meets/{meet['meet_id']}/roster"
    driver.get(meet_url)
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
    return result


if __name__ == "__main__":
    liftingcast = LiftingCast()
    liftingcast.fetch_meets()
    pool = Pool(10)
    lifters_for_each_meet = pool.map(fetch_lifters_from_meet, liftingcast.meets[:10])
    all_lifters = [lifter for meet in lifters_for_each_meet for lifter in meet]
    print(len(all_lifters))
