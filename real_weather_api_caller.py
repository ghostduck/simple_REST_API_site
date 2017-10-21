import requests
import sqlite3
import json
from datetime import datetime
from sample_weather_api_caller import SampleWeatherAPICaller

# IMPORTANT: Open Weather only allows 1 call per 10 MINUTES, so the worker thread needs to adjust accordingly

# Possible solutions:
# Because we only have 1 call every 10 minutes, we have to ...
#
# 1. Implement a fake server with the same output format, so that we can call it without such limit
# 2. Use group call (1 call for 3 ids is counts 3 uses), still 10 minutes per call
# 3. Use fake sample data every minute, since they fixed city ids in group call
# Method 2 is used in this class

class RealWeatherAPICaller(SampleWeatherAPICaller):

    def retrieve_data(self):
        # use real API and real key
        # IMPORTANT: USE REAL API LINK BEFORE FINISHING this project
        #REAL_OW_API = "http://api.openweathermap.org/data/2.5/group?id={city_ids}&appid={api_key}&units=metric"
        FAKE_OW_API = "http://samples.openweathermap.org/data/2.5/group?id=524901,703448,2643743&units=metric&appid=b1b15e88fa797225412429c1c50c122a1"

        ids = [self.__class__.SG_ID, self.__class__.HK_ID]
        city_ids = ",".join(map(lambda x:str(x), ids))
        url = FAKE_OW_API.format(city_ids=city_ids, api_key=self.api_key)

        try:
            group_data = self._processGroupData(url)
        except ValueError as e:
            # JSON errors
            print("Error when reading JSON")
            print(e)
            raise e

        time_str = datetime.now().isoformat(timespec='seconds')
        for d in group_data:
            print("Going to add new record to db after retrieval at {}".format(time_str))
            self._insert_db(time_str, d)

    def _processGroupData(self, group_url):
        # return list of processed tuples
        raw_group_data = requests.get(group_url).json()["list"]
        return list(self._parse_single_city_data(d) for d in raw_group_data)


