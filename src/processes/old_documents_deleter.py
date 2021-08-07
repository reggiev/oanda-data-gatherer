import time
from datetime import datetime, timedelta

import schedule
from src.endpoints.util import get_deletion_cutoff
from src.processes.system_event_writer import system_event
from src.stateful_connectors.mongo_connector import delete_documents


def delete_old_documents():
    schedule.every(15).minutes.at(":40").do(_delete_old_documents)

    while True:
        schedule.run_pending()
        time.sleep(1)


def _delete_old_documents():
    print("Deleting old documents")

    dt = datetime.now()

    expired_candles_query = {
        "$or": [
            {"$and": [
                {"granularity": "M"},
                # 10 years
                {"time": {"$lte": get_deletion_cutoff(hours=87600)}}
            ]},
            {"$and": [
                {"granularity": "D"},
                {"time": {"$lte": get_deletion_cutoff(hours=35040)}}  # 4 years
            ]},
            {"$and": [
                {"granularity": "H12"},
                {"time": {"$lte": get_deletion_cutoff(hours=2880)}}  # 4 months
            ]},
            {"$and": [
                {"granularity": "H1"},
                {"time": {"$lte": get_deletion_cutoff(hours=960)}}  # 40 days
            ]},
            {"$and": [
                {"granularity": "M5"},
                {"time": {"$lte": get_deletion_cutoff(hours=72)}}  # 3 days
            ]}
        ]
    }

    delete_documents("candle", expired_candles_query)

    expired_system_actions = {
        "time": {"$lte": datetime.now() - timedelta(days=30)}}
    delete_documents("system_action", expired_system_actions)

    prices_cutoff = get_deletion_cutoff(hours=5)
    expired_prices = {"time": {"$lte": prices_cutoff}}
    delete_documents("price", expired_prices)

    expired_metrics = {"time": {"$lte": get_deletion_cutoff(hours=250)}} # approx 10 days
    delete_documents("metric", expired_metrics)

    system_event("data_analyst", "_delete_old_documents", dt, remarks={"start": dt,
                                                                       "end": datetime.now()})
    print("Done deleting documents")
