# a626-flask-api

# About this API
This is a Flask API that uses ADSB flight tracking data, stored in the class_datapoints MySQL table, and has three endpoints (schemas below): /getData, /countInPolygon, and /getAvgSpeedByFlight.
Description of endpoints:
- getData: returns data points between a start and end date/time [url: `http://127.0.0.1:5000/getData?key=123&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15`]
- countInPolygon: returns the number of data points inside a polygon (longitude latitude points) [url: `http://127.0.0.1:5000/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41,-74 42`]
-getAvgSpeedByFlight: returns the average ground speed for each flight [url: `http://127.0.0.1:5000/getAvgSpeedByFlight?key=123&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00`]


How to Run It:
- install packages: "pip install flask requests pymysql pyyaml"
- create a config.yml file with connection details to MySQL - needs to have MySQL host, port, username, password, and database. List in .gitignore so the password isn't uploaded to GitHub
- start the API in terminal: "python main.py" (leave terminal open)
- open second terminal: "python test-client.py" (sends valid request and wrong key request to each endpoint)

Authentication and Logging:
- "leblaneg_auth" stores the API keys that are allowed to use the API; key 123 is stored here
- "leblaneg_api_logs" records every request (even the failed ones); stores response status (200 = ok, 400 = missing or invalid input, 429 = auth error), endpoint, key used, and date/time



## JSON schemas

## /getData

```json
{
  "type": "object",
  "properties": {
    "code":    { "type": "integer", "description": "1 = success, 0 = failed" },
    "msg":     { "type": "string",  "description": "Message that describes the result or reason for failed request" },
    "req":     { "type": "string",  "description": "The endpoint that was requested" },
    "sqltime": { "type": "number",  "description": "Time in seconds the SQL query took to run" },
    "results": {
      "type": "array",
      "description": "Data points between start and end, ordered by date_time (limit is 500)",
      "items": {
        "type": "object",
        "properties": {
          "dpid":        { "type": "integer" },
          "date_time":   { "type": "string" },
          "hex":         { "type": "string" },
          "flight_num":  { "type": "string" },
          "squawk":      { "type": "integer" },
          "lat":         { "type": "string" },
          "lon":         { "type": "string" },
          "geo_point":   { "type": "string", "description": "Binary location data, converted to text; use lat/lon instead" },
          "fid":         { "type": "integer" },
          "gs":          { "type": "string" },
          "alt_gps":     { "type": "integer" },
          "alt_baro":    { "type": "integer" },
          "cat":         { "type": "string" },
          "track":       { "type": "string" },
          "nav_heading": { "type": ["string", "null"] }
        }
      }
    },
    "num_results": { "type": "integer", "description": "Number of data points returned" }
  },
  "required": ["code", "msg", "req", "sqltime"]
}
```

## /countInPolygon

```json
{
  "type": "object",
  "properties": {
    "code":    { "type": "integer", "description": "1 = success, 0 = failed" },
    "msg":     { "type": "string",  "description": "Message that describes the result or reason for failed request" },
    "req":     { "type": "string",  "description": "The endpoint that was requested" },
    "sqltime": { "type": "number",  "description": "Time in seconds the SQL query took to run" },
    "results": { "type": "integer", "description": "Number of data points inside the given polygon" }
  },
  "required": ["code", "msg", "req", "sqltime"]
}
```


## /getAvgSpeedByFlight

```json
{
  "type": "object",
  "properties": {
    "code":    { "type": "integer", "description": "1 = success, 0 = failed" },
    "msg":     { "type": "string",  "description": "Message that describes the result or reason for failed request" },
    "req":     { "type": "string",  "description": "The endpoint that was requested" },
    "sqltime": { "type": "number",  "description": "Time in seconds the SQL query took to run" },
    "results": {
      "type": "array",
      "description": "Average ground speed for each flight, ordered by flight_num (limit is 500). Filtered by start/end if both are given - otherwise uses all data.",
      "items": {
        "type": "object",
        "properties": {
          "avg_speed":  { "type": "string", "description": "Average ground speed (gs) for the flight" },
          "flight_num": { "type": "string", "description": "Flight number; may be blank for aircraft with no callsign" }
        }
      }
    },
    "num_results": { "type": "integer", "description": "Number of flights returned" }
  },
  "required": ["code", "msg", "req", "sqltime"]
}
```