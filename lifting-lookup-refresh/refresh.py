import pandas as pd
from datetime import datetime

from lifting_cast import LiftingCast
from dynamo import DynamoLifter, DynamoLifterUpdate


def refresh():
    # fetch lifters
    print("Initializing LiftingCast")
    L = LiftingCast()
    print("Fetching meets")
    meets = L.fetch_meets()
    print("Fetching lifters")
    lifters = L.fetch_lifters(meets)

    scraped_lifters = pd.DataFrame(lifters)

    # lifters that we are currently storing
    print("Fetching lifters from dynamo")
    aws_lifter = DynamoLifter()
    stored_lifters = aws_lifter.get_lifters()

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
        aws_lifter.delete_lifters(lifters_to_delete)

    # insert any lifters we scraped that we are currently not storing
    print(f"{len(lifters_to_insert.index)} lifters to insert")
    if "lifter_id" in lifters_to_insert.columns:
        aws_lifter.insert_lifters(lifters_to_insert)

    # make note of the update we just did
    print(f"recording update datetime")
    aws_lifter_update = DynamoLifterUpdate()
    aws_lifter_update.insert_lifter_update(
        str(datetime.now()), len(lifters_to_insert.index), len(lifters_to_delete.index)
    )

    # all done
    print("DONE")
    return 0


refresh()
