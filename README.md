# Simple REST API Site
Very small toy project of building RESTful API, written in Python using Python Web Server Gateway Interface ([PEP 3333](https://www.python.org/dev/peps/pep-3333/))

No framework is used, everything in Pure Python3.

This is my second interview test of writing a RESTful API + α recently

# Instructions
Clone this repo, then copy **_config/template.json_** to **_config/keys.json_**.

After that, paste your [OpenWeatherMap API key](https://home.openweathermap.org/api_keys) to replace the value of weatherkey.

Once the key setup is completed, the server is ready to use.

Start the server by executing *server.py*. The server should be available at http://127.0.0.1:8000/weather .

In order to obtain data from this RESTful server, you need to provide the following parameters using *GET*:
- city  : currently only has 'hk' or 'sg'. Case dosen't matter. Other cities will return a 404 not found
- start : Timestamp in format of YYYY-MM-DDTHH:MM:SS (Example: 2017-10-21T23:35:45)
- end   : Same as above. Make sure start is before end, otherwise a 400 error will be returned

URL example: http://127.0.0.1:8000/weather?city=HK&start=1970-01-01T12%3A00%3A00&end=2017-10-21T21%3A19%3A09

This will try to get all the data starting from 1970-1-1 12:00:00 to 2017-10-21 21:19:09

About the city parameter:
You can add more by adding entries to the table of **city_shortname** in database. 
The city id and shortname needs to follow the one in OpenWeatherMap API reference ([here, city.list.json.gz](http://bulk.openweathermap.org/sample/)), or it will not work at all.

Once the server is running, you can run *client.py* to try obtaining data from server. It returns a JSON of records.

# WARNING 
For Free plans, you can only call the API once per 10 minutes only. [Source](https://openweathermap.org/appid)

As a result, if you restart the server too frequently (API call will be issued on start of server), the API key will be blocked for a long period.

One of the requirement is to call the API every minute. In order to not to get banned, I have to set a "FAKE" mode to simulate the process of continously calling.

Change the variable **fake** to **True** in *server.py* `fake = True` to use fake mode, which will only get sample/fake data from API.

