#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server
import re
import json
from datetime import datetime
from sample_weather_api_caller import SampleWeatherAPICaller, CityNotFoundError
from real_weather_api_caller import RealWeatherAPICaller
from urllib.parse import parse_qs
import threading

fake = False
# data source of city weather
cw_source = RealWeatherAPICaller()
if fake:
    print("Fake mode now, use SampleWeatherAPICaller as source")
    cw_source = SampleWeatherAPICaller() # fake one

# handlers for errors
def city_not_found(environ, start_response):
    status = '404 Not Found'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    # ret = [("%s: %s\n" % (key, value)).encode("utf-8")
       # for key, value in environ.items()]
    # return ret

    return ["404 City not found".encode("utf-8")]

# intended use for data source error, currently should only be used when forced error
def internal_error(environ, start_response):
    status = '500 System Errors'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return ["500 System Errors".encode("utf-8")]

def general_value_error(environ, start_response):
    status = '400 Bad Request'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    error_msg = environ["custom_error_message"]
    return [error_msg.encode("utf-8")]

def not_found(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])

    # ret = [("%s: %s\n" % (key, value)).encode("utf-8")
       # for key, value in environ.items()]
    # return ret

    return ['404 Page Not Found'.encode("utf-8")]

def favicon(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', "data:image/png;")]

    with open("favicon.ico", 'br') as file:
        f = file.read()

    start_response(status, headers)
    return [f]

def city_weather_full_view(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=utf-8')]

    try:
        data_source = cw_source

        # parse query string
        q_s = environ.get('QUERY_STRING')
        if not q_s:
            raise ValueError("Please provide parameter of city, start and end")

        query = parse_qs(q_s, strict_parsing=True)
        # normally will raise if there is no query string, but we handled it above

        for k,v in query.items():
            # only want 1 thing from query string
            query[k] = v[0]

        start = query.get("start")
        end = query.get("end")
        city_short_name = query.get("city")

        if (start is None) or (end is None):
            raise ValueError("Need both start and end date")

        start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

        if start > end:
            raise ValueError("Start time is after End time")

        if (city_short_name is None):
            raise ValueError("City shortname is not provided")

        city_short_name = city_short_name.lower()

        # get city weather data
        data = data_source.get_db_records(city_short_name, start, end)

        # output
        start_response(status, headers)
        return [json.dumps(data).encode("utf-8")]

    # Custom errors
    except CityNotFoundError:
        return city_not_found(environ, start_response)
    except ValueError as e:
        environ["custom_error_message"] = repr(e)
        return general_value_error(environ, start_response)


class APIApplication(object):
    def __init__(self, application):
        self.application = application
        self.setup_routes()

    def setup_routes(self):
        # map route to a view
        self.routes = [
           # e.g. /weather
           (r'^\/weather$', city_weather_full_view),
           (r'^\/favicon.ico', favicon)
        ]

    def __call__(self, environ, start_response):
        # main logic for the API Application
        # parse path, then fail/show object

        # https://bugs.python.org/issue16679
        # Can't deal with unicode directly, needs to be ISO-8859-1 -> Byte -> Unicode
        path = environ.get('PATH_INFO')

        npath = bytearray(path, 'iso-8859-1').decode('utf8')
        handler = self.find_route(npath)

        return handler(environ, start_response)

    def find_route(self, path):
        # no checking for conflicting routes currently

        for (pattern, handler) in self.routes:
            if re.compile(pattern, re.UNICODE).search(path):
                return handler

        return not_found


def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]

    start_response(status, headers)

    # won't execute in browser anyway, not really a JSON object, but whatever
    # return ["<script>alert('hacked world')</script>\n".encode("utf-8")]

    # for debugging
    ret = [("%s: %s\n" % (key, value)).encode("utf-8")
           for key, value in environ.items()]
    return ret

def keep_retrieve_data():
    print("Going to retrieve data from external source now")
    cw_source.retrieve_data()

    t = threading.Timer(630.0, keep_retrieve_data)
    if fake:
        print("Fake mode now, can repeat retrieve data in every 30 secs")
        t = threading.Timer(30.0, keep_retrieve_data) # for fake one

    t.daemon = True
    t.start()

if __name__ == '__main__':
    print("WARNING: Keep restarting server when fake is False can result in BAN of the API Key")
    timerThread = threading.Thread(target=keep_retrieve_data)
    timerThread.daemon = True
    timerThread.start()

    with make_server('', 8000, APIApplication(simple_app)) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
