import math

import requests
from fastapi import HTTPException


def check_server_health(url: str):
    response = requests.get(url)
    return response.status_code == 200


def find_lightest_instance(servers_load: dict):
    lowest_key = None
    lowest = math.inf
    for key, value in servers_load.items():
        health = check_server_health(key)
        if not health:
            servers_load[key] = 0
            continue
        if value < lowest:
            lowest_key = key
            lowest = value

    if lowest_key is None:
        raise HTTPException(503, detail="No server model available")
    return lowest_key
