# My design notes

So here is my explanation of codes.

# About the server

I have written that server for another interview test quite recently. The codes are in [this commit](https://github.com/ghostduck/simple_REST_API_site/commit/ba24aef30b6f08c593d37c5ff99afad43896beb1)

That test was to implement a RESTful server providing a Weather service API. What a coincidence!

My current Windows machine is running out of space and can't install too many extra things, so I have to do everything in Pure Python.
I hope it runs well on your Linux machines.

# server.py
The router + controller is in `class APIApplication()` in `server.py`. Since we have only 1 route this time, the route is very simple.

The controller + view which returns the JSON is in `def city_weather_full_view()` in `server.py`. It checks the parameters (query string), raise exceptions then redirect to other views if needed.

The model is `cw_source`, which can be `RealWeatherAPICaller` or `SampleWeatherAPICaller` by turning fake mode on or off.

For the requirement of "calling API to update entries in database", it is achieved by making another thread to update every 10 minutes in `keep_retrieve_data()`.

Before the server runs the HTTP server, the `timerThread` will start first. It will call `keep_retrieve_data()`. `keep_retrieve_data()` will create another timed thread (`threading.Timer`) to call itself. 

Both `timerThread` and `keep_retrieve_data()` are daemon, so they will all ends when the main thread (http server) ends.

The server will end by pressing Ctrl+C to interrupt.

# SampleWeatherAPICaller and RealWeatherAPICaller

`SampleWeatherAPICaller` is the base class of `RealWeatherAPICaller`. The sample caller is the fake data caller actually.

It has 2 main "public" methods, namely `retrieve_data()` and `get_db_records()`.

`retrieve_data()` is overwritten in `RealWeatherAPICaller` so that it provides real data. In `SampleWeatherAPICaller`, it will only put the values in sample data to database.

`get_db_records()` is called by server, and remains the same for both callers.

# Database
I don't have any SQL server installed in my current machine so I use SQLite3, which is built-in in Python3.

This time only 2 tables are needed, namely `weather_records` and `city_shortname`.

`weather_records` store the records from API, and can be called by http server.

`city_shortname` stores the shortname and id in OpenWeatherMap. (check README.md for details)

I feel that the current database schema is good enough for this toy project, but not sure if it is optimal or not.
