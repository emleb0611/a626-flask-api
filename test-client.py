import requests, json



#/getData
#valid request:
url = 'http://127.0.0.1:5000/getData?key=123&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15'
r = requests.get(url)
resp = json.loads(r.text)
print('getData - valid:', resp['code'], resp['msg'], resp['sqltime'])
print(resp['num_results'], 'results')

#wrong key:
url = 'http://127.0.0.1:5000/getData?key=999&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15'
r = requests.get(url)
resp = json.loads(r.text)
print('getData - wrong key:', resp['code'], resp['msg'], resp['sqltime'])



#/countInPolygon
#valid request
url = 'http://127.0.0.1:5000/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41,-74 42'
r = requests.get(url)
resp = json.loads(r.text)
print('countInPolygon - valid:', resp['code'], resp['msg'], resp['sqltime'])
print(resp['results'], 'points in polygon')

#wrong key
url = 'http://127.0.0.1:5000/countInPolygon?key=999&polygon=-74 42,-75 39,-74 41,-74 42'
r = requests.get(url)
resp = json.loads(r.text)
print('countInPolygon - wrong key:', resp['code'], resp['msg'], resp['sqltime'])



#/getAvgSpeedByFlight
#valid request:
url = 'http://127.0.0.1:5000/getAvgSpeedByFlight?key=123&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00'
r = requests.get(url)
resp = json.loads(r.text)
print('getAvgSpeedByFlight - valid:', resp['code'], resp['msg'], resp['sqltime'])
print(resp['num_results'], 'results')

#wrong key
url = 'http://127.0.0.1:5000/getAvgSpeedByFlight?key=999&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00'
r = requests.get(url)
resp = json.loads(r.text)
print('getAvgSpeedByFlight - wrong key:', resp['code'], resp['msg'], resp['sqltime'])
