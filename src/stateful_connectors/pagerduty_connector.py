import requests
import os
import json


def get_pagerduty_token():
    return os.environ.get("pagerduty_token", "")


def get_pagerduty_url():
    return os.environ.get("pagerduty_url", "")


def pagerduty_email():
    return os.environ.get("pagerduty_email", "")


def create_pagerduty_header():
    email = pagerduty_email()

    return {
        "Authorization": get_pagerduty_token(),
        "Accept": "application/vnd.pagerduty+json;version=2",
        "From": email,
        "Content-Type": "application/json"
    }


def add_incident_note(pg_id):
    header = create_pagerduty_header()
    url = get_pagerduty_url() + "incidents/{id}/notes".format(id=pg_id)
    note = {
        "note": {
            "content": "Issue was raised again."
        }
    }

    requests.post(url=url, headers=header, json=note)


def active_incident(title):
    header = create_pagerduty_header()
    url = get_pagerduty_url() + "incidents"
    active_incidents = {
        "statuses": ["triggered", "acknowledged"]
    }

    res = requests.get(url=url, headers=header, json=active_incidents)

    for i in res.json()["incidents"]:
        if i["title"] == title:
            #  Update that this incident is raised again
            add_incident_note(i["id"])
            return True
    return False


# TODO determine design for service type incidents
# TODO Add the stack trace of the error to the pagerduty incident
def raise_pagerduty_incident(title, service=None, details=""):
    # Determines if the incident is currently active, add note only if active
    if active_incident(title):
        return "Incident already active in Pagerduty"
    else:
        # Incident is not yet existing
        header = create_pagerduty_header()
        url = get_pagerduty_url() + "incidents"

        sample = {
            "incident": {
                "type": "Outage",
                "title": title,

                "service": {
                    "id": "PEEK0L9",
                    "type": "service_reference"
                },
                "body": {

                    "type": "incident_body",
                    "details": details
                }
            }
        }

        res = requests.post(url=url, headers=header, json=sample)
        rmsg = "Raised pagerduty incident. Response code: " + str(res.status_code)

        if res.status_code != 201:
            rmsg += "\n```" + str(json.dumps(res.json(), indent=2)) + "```"

        return rmsg
