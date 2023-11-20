from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

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
