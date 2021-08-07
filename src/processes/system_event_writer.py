from src.stateful_connectors.mongo_connector import pymwriter


def system_event(app, method, action_time, remarks):
    pymwriter("system_action", [{
        "app": app,
        "method": method,
        "time": action_time,
        "remarks": remarks,
        "_id": str(action_time) + method
    }])