import json,pymysql,time
from flask import Flask
from flask import request,redirect
import datetime
import yaml


app = Flask(__name__)

db_config = None
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)
    db_config = config['mysql']     

def auth(token):
    if token is None:
        return False
    conn = pymysql.connect(**db_config) #setup our credentials
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM leblaneg_auth WHERE `token` = %s;'
    cur.execute(sql,(token))
    results = cur.fetchall()
    if len(results) == 1:
        return True
    else:
        return False

def log(token,endpoint,response):
    conn = pymysql.connect(**db_config) #setup our credentials
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'INSERT INTO `leblaneg_api_logs` (`endpoint`,`token`,`response`,`dt`) VALUES (%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(sql,(endpoint,token,response,dt))


@app.route("/", methods=['GET','POST'])
def root():
    res = {} 
    res['code'] = 2
    res['msg'] = 'No endpoint specified'
    res['req'] = '/'
    return json.dumps(res,indent=4)
    #return '<b>hello</b>'

@app.route("/sum", methods=['GET','POST'])
def sum():
    res = {}
    res['req'] = '/sum'
    n1 = request.args.get('n1')
    n2 = request.args.get('n2')
    n1f = None
    n2f = None
    try:
        n1f = float(n1)
        n2f = float(n2)
    except Exception as e:
        print(str(e))
        pass
    if n1f is not None and n2f is not None:
        res['sum'] = n1f + n2f
        res['code'] = 2
        res['msg'] = 'ok'
    else:
        res['sum'] = None
        res['code'] = 1
        res['msg'] = 'n1 and n2 must be numeric'
        log(request.args.get('key'),res['req'],'429')
    log(request.args.get('key'),res['req'],'200')
    return json.dumps(res,indent=4)
@app.route("/searchCountry", methods=['GET','POST'])
def searchCountry():
    res = {} 
    res['req'] = '/searchCountry'
    if not auth(request.args.get('key')):
        res['code'] = 1
        res['msg'] = 'auth error'
        log(request.args.get('key'),res['req'],'429')
        return json.dumps(res,indent=4)
    
    country_term = request.args.get('country')
    if country_term is None:
        res['code'] = 1
        res['msg'] = 'country needs to be provided.'
        return json.dumps(res,indent=4)
    conn = pymysql.connect(**db_config) #setup our credentials
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM class_airlines WHERE `country` LIKE %s ORDER BY `country`;'
    st = f'%{country_term}%'
    print(sql,st)
    cur.execute(sql,(st))
    res['code'] = 0
    res['msg'] = 'ok'
    items = []
    for row in cur:
        item = {}
        item['icao'] = row['icao']
        item['country'] = row['country']
        item['airline_name'] = row['airline']
        items.append(item)

    res['results'] = items
    res['num_results'] = len(items)
    log(request.args.get('key'),res['req'],'200')
    return json.dumps(res,indent=4)


#building /getData

@app.route("/getData", methods=['GET'])
def getData():
    res = {}
    res['req'] = '/getData'
    res['sqltime'] = 0          
    key = request.args.get('key')

    
    if not auth(key):
        res['code'] = 0       #number that means failed, 1 = success
        res['msg'] = 'auth error'
        log(key, res['req'], '429')   #status code for "not allowed"
        return json.dumps(res, indent=4)

    
    start = request.args.get('start')   #from URL
    end = request.args.get('end')
    if start is None or end is None:
        res['code'] = 0
        res['msg'] = 'start and end dates are required'            #alert about whats missing (start and end dates are mandatory)
        log(key, res['req'], '400')   #status code for "bad request"
        return json.dumps(res, indent=4)

    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM `class_datapoints` WHERE `date_time` BETWEEN %s AND %s ORDER BY `date_time` LIMIT 0,500;'     #uses the first query with %s, limits results to 500
    t0 = time.time()
    cur.execute(sql, (start, end))
    rows = cur.fetchall()
    res['sqltime'] = time.time() - t0

    
    res['code'] = 1             # spec: what number means "success"?
    res['msg'] = 'ok'
    res['results'] = rows
    res['num_results'] = len(rows)
    log(key, res['req'], '200')     # status code for success
    return json.dumps(res, indent=4, default=str)


#building /countinpolygon
@app.route("/countInPolygon", methods=['GET'])
def countInPolygon():
    res = {}
    res['req'] = '/countInPolygon'    
    res['sqltime'] = 0
    key = request.args.get('key')

    
    if not auth(key):
        res['code'] = 0
        res['msg'] = 'auth error'
        log(key, res['req'], '429')
        return json.dumps(res, indent=4)

    
    polygon = request.args.get('polygon')      #from URL
    if polygon is None:
        res['code'] = 0
        res['msg'] = 'needs polygon to proceed'        #message if key(polygon) is missing
        log(key, res['req'], 400)
        return json.dumps(res, indent=4)

    
    shape = f'Polygon(({polygon}))'

    # 4. Run the query and time it
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT COUNT(*) AS count FROM `class_datapoints` WHERE st_within(geo_point, ST_GeomFromText(%s,0));'
    t0 = time.time()
    try:
        cur.execute(sql, (shape,))         #variable that fills %s in sql
        row = cur.fetchone()
    except Exception as e:
        res['code'] = 0
        res['msg'] = 'invalid polygon: ' + str(e)
        log(key, res['req'], '400')
        return json.dumps(res, indent=4)
    res['sqltime'] = time.time() - t0

    
    res['code'] = 1
    res['msg'] = 'ok'
    res['results'] = row['count']
    log(key, res['req'], '200')
    return json.dumps(res, indent=4, default=str)

#building /getAvgSpeedByFlight endpoint

@app.route("/getAvgSpeedByFlight", methods=['GET'])
def getAvgSpeedByFlight():
    res = {}
    res['req'] = '/getAvgSpeedByFlight'
    res['sqltime'] = 0
    key = request.args.get('key')

    
    if not auth(key):
        res['code'] = 0
        res['msg'] = 'auth error'
        log(key, res['req'], '429')
        return json.dumps(res, indent=4)

    #optional start and end dates
    start = request.args.get('start')
    end = request.args.get('end')
    #send error if only one date is given:
    if (start is None) != (end is None):
        res['code'] = 0
        res['msg'] = "provide both start AND end dates, or no dates at all"      #explanation error message
        log(key, res['req'], '400')
        return json.dumps(res, indent=4)

    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if start is not None:
        sql = 'SELECT AVG(gs) AS avg_speed, `flight_num` FROM `class_datapoints` WHERE `date_time` BETWEEN %s AND %s GROUP BY `flight_num` ORDER BY `flight_num` LIMIT 0,500' #limits to 500
        params = (start, end)
    else: #same SQL query but WHERE and BETWEEN part is removed
        sql = 'SELECT AVG(gs) AS avg_speed, `flight_num` FROM `class_datapoints` GROUP BY `flight_num` ORDER BY `flight_num` LIMIT 0,500;'     
        params = ()
    t0 = time.time()
    cur.execute(sql, params)
    rows = cur.fetchall()
    res['sqltime'] = time.time() - t0

   
    res['code'] = 1
    res['msg'] = 'ok'
    res['results'] = rows
    res['num_results'] = len(rows)
    log(key, res['req'], '200')
    return json.dumps(res, indent=4, default=str)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)