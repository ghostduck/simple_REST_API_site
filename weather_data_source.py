#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The (fake) data source of weather API
# dict is the format for city weather
import random
import json
from datetime import datetime

CITY_DATA_PATH="cityname.json"

class CustomError(Exception):
     def __init__(self, value=""):
         self.value = value
     def __str__(self):
         return repr(self.value)

class DataUnavailableError(CustomError):
    pass

class CityNotFoundError(CustomError):
    pass

class WeatherDataSource(object):
    def __init__(self):
        self.setup()

    def setup(self):
        with open(CITY_DATA_PATH, encoding="utf-8") as fp:
            data = json.load(fp)

        self.setupReverseIndex(data)
        self.setupDisplayNameLookup(data)

    def setupReverseIndex(self, data):
        self.reverseIndex = {}
        for arr in data:
            i = int(arr[0])
            for name in arr[1:]:
                # case doesn't matter
                self.reverseIndex[name.lower()] = i

    def setupDisplayNameLookup(self, data):
        self.displayLookup = {}
        for arr in data:
            self.displayLookup[int(arr[0])] = arr[1]

    def unitConversion(self, weatherStat, optionsDict={}):
        newweatherStat = weatherStat.copy()
        unitDict = optionsDict.get("format", {})

        # currently load "format" only
        for k,v in unitDict.items():
            k=k.strip().lower()
            v=v.strip().lower()

            if k == "temperature":
                if v == "fahrenheit":
                    convert = lambda x: x * 9 / 5 + 32
                elif v == "customrule1":
                    # example of custom conversion
                    convert = lambda x: x * 3 - 5
                elif v == "celsius":
                    # do nothing
                    convert = lambda x:x
                else:
                    raise ValueError("Unknown unit option of {} in {}".format(v,k))
                newweatherStat[k] = convert(float(newweatherStat[k]))

            # add other conversion methods for other fields here

        return newweatherStat

    def generateCityContent(self, city):
        city_id = self.getIdfromCityName(city)
        return {
            "city_id" : city_id,
            "city_name" : self.getCityDisplayName(city_id),
            # should really consider time zone
            "city_current_time" : str(datetime.now())
        }

    def generateRandomWeather(self, error=False):
        if error:
            raise DataUnavailableError("Simulate data source unavailable")

        return {
            "temperature" : random.uniform(-40, 40), # degree celsius
            "humidity" : random.uniform(0, 100), # %
            "windspeed" : random.uniform(0, 15), # mph
            "status" : random.choice(["Partly cloudy", "Light rain", "Thunderstorm", "Sunny", "Sandstorm"]),
            "atmopressure" : random.uniform(28, 30) #in-Hg
        }

    def getCityDisplayName(self, city_id):
        return self.displayLookup[city_id]

    def getIdfromCityName(self, name):
        try:
            return self.reverseIndex[name]
        except KeyError:
            raise CityNotFoundError("Incorrect city name")

    def getCityData(self, name, optionsDict={}, error=False):
        name = name.lower()
        return {
            "city" : self.generateCityContent(name),
            "format": optionsDict,
            "weather" : self.unitConversion(self.generateRandomWeather(error), optionsDict)
        }

