import multiprocessing as mp
import os
import re
import time
import traceback

from src.endpoints.account import get_instruments
from src.endpoints.general import is_market_hours

from src.processes.current_prices_fetcher import fetch_current_prices
from src.processes.historical_candlestick_fetcher import fetch_historical_candlestick
from src.processes.old_documents_deleter import delete_old_documents
from src.processes.system_event_writer import system_event

from src.stateful_connectors.pagerduty_connector import raise_pagerduty_incident
from src.stateful_connectors.slack_connector import send_msg_to_slack_channel


class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            # TODO, this exception handling will fail if the process fails during startup
            # the parent thread will not know that it failed to start
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            raise e

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

def process_scheduler(job):
    pass


if __name__ == "__main__":
    url = os.environ.get('oanda_rest_url', "")
    account_id = os.environ.get('account_id', "")

    instruments = None
    pg_raised = False
    ic = 0    

    while True:
        if is_market_hours():
            send_msg_to_slack_channel(
                "slack_process_monitor", {"text": "Activating since its market hours."})
            break
        else:
            print("Sleeping since it's not yet market hours.")

        # sleep for 3 mins
        time.sleep(180)

    while True:
        try:
            instruments = get_instruments(instance=url, account_id=account_id)
        except Exception as e:
            ic += 1

            if ic == 4 and not pg_raised:
                i_msg = "Critical, instrument fetching mechanism is failing.\n"
                send_msg_to_slack_channel("slack_process_monitor", {
                                          "text": i_msg + "```" + str(e) + "```"})

            elif ic > 30 and not pg_raised:
                i_msg = "Critical, instrument fetching mechanism is failing.\n"
                pg_msg = raise_pagerduty_incident(i_msg, None, str(e))
                send_msg_to_slack_channel(
                    "slack_process_monitor", {"text": pg_msg})
                pg_raised = True

        if instruments:
            break
        time.sleep(1)

    # Create a list with instrument names
    ins_name_list = [i["name"] for i in instruments]
    ins_list_str = ','.join([str(elem) for elem in ins_name_list])

    jobs = [
        {
            "name": "delete_old_documents",
            "target": delete_old_documents,
            "params": (),
            "schedule": {
                "every_minute": 15,
                "minute_trigger": ":40"
            }
        },
        {
            "name": "fetch_current_prices",
            "target": fetch_current_prices,
            "params": (ins_list_str, url, account_id)
        },
        # {
        #     "name": "fetch_historical_candlestick_M5",
        #     "target": fetch_historical_candlestick,
        #     "params": (ins_name_list, ["M5"], url, account_id)
        # },
        {
            "name": "fetch_historical_candlestick_H1",
            "target": fetch_historical_candlestick,
            "params": (ins_name_list, ["H1"], url, account_id)
        },
        {
            "name": "fetch_historical_candlestick_H12",
            "target": fetch_historical_candlestick,
            "params": (ins_name_list, ["H12"], url, account_id)
        },
        {
            "name": "fetch_historical_candlestick_D_M",
            "target": fetch_historical_candlestick,
            "params": (ins_name_list, ["D", "M"], url, account_id)
        },
        # {
        #     "name": "compute_chartist_prediction_scorer",
        #     "target": compute_chartist_prediction_scorer,
        #     "params": ()
        # }
        # {
        #     "name": "compute_opportunistic_slotted_metric",
        #     "target": compute_opportunistic_slotted_metric,
        #     "params": (ins_name_list,)
        # },
        # {
        #     "name": "compute_frequent_prices",
        #     "target": compute_frequent_prices,
        #     "params": (instrument_name_list,)
        # },
        # {
        #     "name": "compute_bruteforce_correlation_metric",
        #     "target": compute_bruteforce_correlation_metric,
        #     "params": (instrument_name_list,)
        # }
    ]

    sleeper = 3
    process_started = 0
    while True:
        process_started = 0
        
        # Loop through the jobs list
        for j in range(0, len(jobs)):
            # If process not in row, start the process
            if "process" not in jobs[j]:
            # Start the process if it has not yet started
                send_msg_to_slack_channel("slack_process_monitor", 
                {"text": "Starting " + jobs[j]["name"]})

                jobs[j]["process"] = Process(target=jobs[j]["target"], args=jobs[j]["params"])
                jobs[j]["process"].name = jobs[j]["name"]
                jobs[j]["process"].start()
                process_started += 1

                jobs[j]["error_count"] = 0
                jobs[j]["raised_incidents"] = 0

                if "error_threshold" not in jobs[j]:
                    jobs[j]["error_threshold"] = 2
                time.sleep(sleeper)

            # Check if the process returned any exception or if the process is still alive
            if jobs[j]["process"].exception or not jobs[j]["process"].is_alive():
                # If an exception if returned, add one to error count
                jobs[j]["error_count"] += 1

                # If error count > error count threshold for the process, msg slack, raise pagerduty
                if jobs[j]["error_count"] > jobs[j]["error_threshold"] and jobs[j]["raised_incidents"] == 0:
                    pgd_msg = """{} is failing.\n Exception: {}.\n Error count: {}
                    """.format(jobs[j]["name"].replace("_", " "),
                    re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', jobs[j]["process"].exception[0].__class__.__name__),
                    jobs[j]["error_count"])
                    details = str(jobs[j]["process"].exception) if jobs[j]["process"].exception \
                        else """No exception message found. Process may have failed to start.
                            Please check the server logs.
                        """
                    ppmsg = raise_pagerduty_incident(pgd_msg, details=details)
                    send_msg_to_slack_channel(
                        "slack_process_monitor", {"text": ppmsg})
                    send_msg_to_slack_channel(
                        "slack_debug_msgs", {"text": pgd_msg})
                    jobs[j]["raised_incidents"] += 1
                    
        time.sleep(sleeper)

        if process_started:
            send_msg_to_slack_channel(
                "slack_process_monitor", {"text": "Total of {} worker processes started.".format(process_started)})

        # TODO Reset process incident awareness