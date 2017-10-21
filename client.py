#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime

API_URL = "http://127.0.0.1:8000/weather"


if __name__ == '__main__':

    print("start testing from client side")

    # normal call
    start_time = datetime(2017, 10, 21, 8, 00, 00).isoformat(timespec='seconds')
    end_time = datetime(2017, 10, 21, 8, 30, 00).isoformat(timespec='seconds')

    normal_payload = {"city": "HK", "start": start_time, "end" : end_time}
    data = requests.get(API_URL, params=normal_payload)
    print(data)
    d = data.json()
    print("These are the weather date of HK from 2017-10-21 8AM to 8:30AM" )
    print(d)

    normal_payload2 = {"city": "SG", "start": start_time, "end" : end_time}
    data = requests.get(API_URL, params=normal_payload2).json()
    print("These are the weather date of SG from 2017-10-21 8AM to 8:30AM" )
    print(data)

    print("For error cases, you should see the status code and True or False, which means expectation is mathced or not")
    # error case: unknown city
    unknown_city_payload = {"city": "NZ", "start": start_time, "end" : end_time}
    status_code = requests.get(API_URL, params=unknown_city_payload).status_code
    # should print 404
    print(status_code, status_code == 404)

    # error case: city not provided
    no_city_payload = {"start": start_time, "end" : end_time}
    status_code = requests.get(API_URL, params=no_city_payload).status_code
    print(status_code, status_code == 400)

    # error case: no start time
    no_start_time_payload = {"city": "SG", "end" : end_time}
    status_code = requests.get(API_URL, params=no_start_time_payload).status_code
    print(status_code, status_code == 400)

    # error case: no end time
    no_end_time_payload = {"city": "HK", "end" : end_time}
    status_code = requests.get(API_URL, params=no_end_time_payload).status_code
    print(status_code, status_code == 400)

    # print everything in HK
    epoch_time = datetime(1970, 1, 1, 12, 0, 0).isoformat(timespec='seconds')
    now_time =  datetime.now().isoformat(timespec='seconds')
    all_payload = {"city": "HK", "start": epoch_time, "end" : now_time}
    data = requests.get(API_URL, params=all_payload).json()
    print("These are all the weather date of HK" )
    print(data)
