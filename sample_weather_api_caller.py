import requests
import sqlite3
import json
from datetime import datetime


# IMPORTANT: Open Weather only allows 1 call per 10 MINUTES, so the worker thread needs to adjust accordingly

# Possible solutions:
# Because we only have 1 call every 10 minutes, we have to ...
#
# 1. Implement a fake server with the same output format, so that we can call it without such limit
# 2. Use group call (1 call for 3 ids is counts 3 uses), still 10 minutes per call
# 3. Use fake sample data every minute, since they fixed city ids in group call
# 3rd method is used here

class CustomError(Exception):
     def __init__(self, value=""):
         self.value = value
     def __str__(self):
         return repr(self.value)

class CityNotFoundError(CustomError):
    pass

class SampleWeatherAPICaller(object):

    API_KEY_PATH = "config/keys.json"
    DB_PATH  = "data/weather_history.db"
    HK_ID = 1819730
    SG_ID = 1880252
    city_id_name_map = {
        "sg"  : SG_ID,
        "hk"  : HK_ID,
        SG_ID : "sg",
        HK_ID : "hk"
    }

    def __init__(self, sample_mode = True):
        self.sample_mode = sample_mode
        self._setup()

    def retrieve_data(self):
        # call API, insert data to DB

        # Note: can't specify format on sample API
        SAMPLE_API = "http://samples.openweathermap.org/data/2.5/weather?id={city_id}&appid=b1b15e88fa797225412429c1c50c122a1"

        sg_sample_url = SAMPLE_API.format(city_id=self.__class__.SG_ID)
        hk_sample_url = SAMPLE_API.format(city_id=self.__class__.HK_ID)

        try:
            raw_sg_data = requests.get(sg_sample_url).json()
            raw_hk_data = requests.get(hk_sample_url).json()
        except ValueError as e:
            # JSON errors
            print("Error when reading JSON")
            print(e)
            raise e

        # sample data always gives id of 2172797, so need to circumvent it this way
        sg_data = self._parse_single_city_data(raw_sg_data)
        hk_data = self._parse_single_city_data(raw_hk_data)

        time_str = datetime.now().isoformat(timespec='seconds')
        print("Going to add new (sample fake) records to db after retrieval at {}".format(time_str))

        self._insert_db(time_str, sg_data, "sg")
        self._insert_db(time_str, hk_data, "hk")

    def get_db_records(self, city,
        start_time=datetime(1970,1,1,12).isoformat(timespec='seconds'),
        end_time=datetime.now().isoformat(timespec='seconds')
        ):
        # return array of matching records

        # setup
        # city is the short name (hk/sg)
        # search city_id from database
        city_id = self._get_city_id_from_db(city)
        # can directly return empty array if invalid city_id is found actually, but just leave it here in case of new cities

        tuple_for_sql =  (city_id, start_time, end_time)
        sql_select_command = r"""
            SELECT record_time, temperature, humidity
            FROM `weather_records`
            JOIN `city_shortname`
            ON `weather_records`.city_id = `city_shortname`.id
            WHERE city_id = ?
            AND datetime(record_time) BETWEEN datetime(?) AND datetime(?)
            ORDER BY datetime(record_time) DESC
        """

        try:
            with sqlite3.connect(self.__class__.DB_PATH) as connection:
                records = connection.execute(sql_select_command, tuple_for_sql).fetchall()
                print("Get data from database successfully")
                return records
        except sqlite3.Error as e:
            print("Errors when getting record from datebase: ")
            print(e.args[0])
            raise e

        # return list of entries, let other classes to turn it to JSON or something else

    def _setup(self):
        # load config and setup other variables for this object
        config = self._load_config()
        self.api_key = str(config['weatherkey'])

        self._setup_db()

    def _load_config(self):
        with open(self.__class__.API_KEY_PATH, 'r', encoding="utf-8") as file:
            return json.load(file)

    def _setup_db(self):
        # All weather attributes can possibly be null, just imagine you add/remove extra attributes like Air Pollution Index
        sql_create_command = r"""
            CREATE TABLE IF NOT EXISTS `weather_records` (
                `city_id`	INTEGER NOT NULL,
                `record_time`	TEXT NOT NULL,
                `temperature`	REAL,
                `humidity`	REAL,
                PRIMARY KEY(`city_id`,`time`)
            );

            CREATE TABLE IF NOT EXISTS `city_shortname` (
                `shortname`	TEXT NOT NULL,
                `id`	INTEGER NOT NULL UNIQUE,
                PRIMARY KEY(`id`)
            );

            INSERT OR IGNORE INTO city_shortname (shortname, id) VALUES ('sg', 1880252), ('hk', 1819730)
            """

        try:
            with sqlite3.connect(self.__class__.DB_PATH) as connection:
                connection.executescript(sql_create_command)
        except sqlite3.Error as e:
            print("Errors when setting up datebase: ")
            print(e.args[0])
            raise e


    def _insert_db(self, time, weather_data, city_name=""):
        # Trick: if city_name is not given, use the one in weather_data, which is weather_data[2]
        # city_name should only be given in this fake API caller

        city_id = self.__class__.city_id_name_map.get(city_name.lower(), weather_data[2])
        tuple_for_sql = (city_id, time, weather_data[0], weather_data[1])

        sql_insert_command = r"""
            INSERT INTO weather_records (city_id, record_time, temperature, humidity) VALUES (?,?,?,?)
        """

        try:
            with sqlite3.connect(self.__class__.DB_PATH) as connection:
                connection.execute(sql_insert_command, tuple_for_sql)
        except sqlite3.Error as e:
            print("Errors when inserting to datebase: ")
            print(e.args[0])
            raise e

    def _parse_single_city_data(self, data):
        weather_data = (data["main"]["temp"], data["main"]["humidity"], data["id"])
        return weather_data

    def _get_city_id_from_db(self, city):
        tuple_for_sql =  (city, )
        sql_select_command = r"""
            SELECT id
            FROM `city_shortname`
            WHERE shortname = ?
        """
        try:
            with sqlite3.connect(self.__class__.DB_PATH) as connection:
                records = connection.execute(sql_select_command, tuple_for_sql).fetchone()
        except sqlite3.Error as e:
            print("Errors when searching city id in datebase: ")
            print(e.args[0])
            raise e

        if records is None:
            raise CityNotFoundError("Cannot find city")
        return records[0]
