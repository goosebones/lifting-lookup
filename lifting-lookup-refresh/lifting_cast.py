from concurrent.futures import ThreadPoolExecutor
import requests
from tqdm import tqdm

number_of_worker_threads = 10


class LiftingCastException(Exception):
    pass


class LiftingCast:
    def __init__(self):
        pass

    def fetch_meets(self):
        res = requests.get("https://liftingcast.com/api/meets").json()["docs"]
        meet_list = [meet for meet in res if meet["showOnHomePage"]]
        return meet_list

    def process_meet(self, meet):
        # lifter documents always start with "l".
        # query only couchdb documents beginning with "l" to avoid downloading other document types
        meet_docs = requests.get(
            f"https://couchdb.liftingcast.com/{meet['_id']}_readonly/_all_docs?include_docs=true&startkey=\"l\"&endkey=\"l\ufff0\""
        )
        meet_docs = meet_docs.json()
        docs = meet_docs["rows"]
        meet_lifters = []
        for doc in docs:
            try:
                if "name" in doc["doc"]:
                    meet_lifters.append(
                        {
                            "lifter_name": doc["doc"]["name"],
                            "lifter_id": doc["id"],
                            "meet_id": meet["_id"],
                            "meet_name": meet["name"],
                            "meet_date": meet["date"],
                        }
                    )
            except Exception as e:
                print(doc)
        return meet_lifters

    def fetch_lifters(self, meet_list):
        lifters = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_meet, meet) for meet in meet_list]
            for future in tqdm(futures, total=len(meet_list)):
                lifters.extend(future.result())
        return lifters
