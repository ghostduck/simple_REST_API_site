#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server
import re
import json
from weather_data_source import WeatherDataSource, DataUnavailableError, CityNotFoundError
from urllib.parse import unquote
#from cgi import parse_qs
from urllib.parse import parse_qs

# data source of city weather
cw_source = WeatherDataSource()

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

    # Simulate forced server side error
    error = False

    try:
        data_source = cw_source

        # parse arguments from environ
        #
        # https://bugs.python.org/issue16679
        # Can't deal with unicode directly, needs to be ISO-8859-1 -> Byte -> Unicode
        path = environ.get('PATH_INFO')
        npath = bytearray(path, 'iso-8859-1').decode('utf8')

        options = {}

        # parse query string
        q_s = environ.get('QUERY_STRING')
        if q_s:
            query = parse_qs(q_s, strict_parsing=True)

            if query.get("error") == ["1"]:
                error = True
                del query["error"]

            for k,v in query.items():
                # only want 1 thing from query string
                query[k] = v[0]

            options["format"] = query

        pattern = r'^\/api\/\d+\/weather\/([^\/]+)+$'
        cityname_searcher = re.compile(pattern, re.UNICODE)
        cityname = cityname_searcher.search(npath).group(1).lower()

        # get city weather data
        data = data_source.getCityData(cityname, options, error)

        # output
        start_response(status, headers)
        return [json.dumps(data).encode("utf-8")]

    except CityNotFoundError:
        return city_not_found(environ, start_response)
    except DataUnavailableError:
        return internal_error(environ, start_response)
    except ValueError as e:
        # print(type(e))
        # print(e.args)
        # most likely an error in unitConversion()
        environ["custom_error_message"] = repr(e)
        return general_value_error(environ, start_response)


class APIApplication(object):
    def __init__(self, application):
        self.application = application
        self.setup_routes()

    def __call__(self, environ, start_response):
        # main logic for the API Application
        # parse path, then fail/show object

        # https://bugs.python.org/issue16679
        # Can't deal with unicode directly, needs to be ISO-8859-1 -> Byte -> Unicode
        path = environ.get('PATH_INFO')

        npath = bytearray(path, 'iso-8859-1').decode('utf8')
        handler = self.find_route(npath)

        return handler(environ, start_response)

    def setup_routes(self):
        # map route to a view
        self.routes = [
           # e.g. /api/1/weather/hk/status
           #(r'^\/api\/\d+\/weather\/\w+\/\w+$', city_weather_attribute_view),

           # e.g. /api/1/weather/warsaw
           #r'^\/api\/\d+\/weather\/[^\/]+$'
           #r'^\/api\/\d+\/weather\/\w+$'
           (r'^\/api\/\d+\/weather\/[^\/]+$', city_weather_full_view),
           (r'^\/favicon.ico', favicon)
        ]

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

if __name__ == '__main__':
    with make_server('', 8000, APIApplication(simple_app)) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
