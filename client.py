#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

HK_API = "http://127.0.0.1:8000/api/1/weather/香港"
#HK_TEMP_API = "http://127.0.0.1:8000/api/1/weather/香港/temperature"
#HK_STATUS_API = "http://127.0.0.1:8000/api/1/weather/hk/status"
HK_API2 = "http://127.0.0.1:8000/api/1/weather/hong kong"
WARSAW_API = "http://127.0.0.1:8000/api/1/weather/warsaw"
RANDOM_API = "http://127.0.0.1:8000/api/1/weather/rancity"
# treated as unknown city for now
FAILCASE_API = "http://127.0.0.1:8000/api/1/weather/london"
# extra closing '/'
FAILCASE2_API = "http://127.0.0.1:8000/api/1/weather/HK/"

if __name__ == '__main__':

    print("start testing from client side")

    # normal call with formatting parameters
    payload = {"temperature": "fahrenheit", "useless": "param"}
    data = requests.get(HK_API, params=payload).json()
    print("{} is having {}".format(data["city"]["city_name"], data["weather"]["status"]) )
    print(data)

    # normal call, support unicode in URL
    data = requests.get(HK_API).json()
    print(data)

    data = requests.get(HK_API2).json()
    print(data)

    data = requests.get(WARSAW_API).json()
    print(data)

    data = requests.get(RANDOM_API).json()
    print(data)

    # error case: unknown city
    status_code = requests.get(FAILCASE_API).status_code
    # should print 404
    print(status_code)

    # simulate server error
    error_payload = {"error": "1"}
    status_code = requests.get(WARSAW_API, params=error_payload).status_code
    # should print 500
    print(status_code)

    # user error in unit conversion
    error_payload2 = {"temperature": "wrongspelling"}
    status_code = requests.get(HK_API2, params=error_payload2).status_code
    # should print 400
    print(status_code)
    
    # almost correct route
    status_code = requests.get(FAILCASE2_API).status_code
    # should print 404
    print(status_code)
