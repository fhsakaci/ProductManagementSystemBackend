from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask import Response
import json
import hashlib


from Database.MongoDatabaseConnection import Database
from utils import utils


logger = utils.set_logger( __name__, __file__ )
logger.info('Server service has been started..' )

dB=Database("localhost",27017)
dB.Connect("sakaci","sakaci","product_management_system")

auth = HTTPBasicAuth()
user = 'luiz'
pw = '123'
users = {
    user: generate_password_hash(pw)
}


app = Flask(__name__)
@app.route('/login', methods=['GET', 'POST'])
@auth.login_required
def login():
    payload = request.json
    username = payload["username"]
    password = payload["password"]
    result = dB.SearchUser("user", username, password)
    if result == False:
        return Response(status=401, mimetype='application/json')
    else:
        return Response(json.dumps({'id':str(result["_id"])}),  status=200, mimetype='application/json')

@app.route('/user', methods=['GET', 'POST'])
@auth.login_required
def user():
    body = request.json
    id = body["id"]
    result = dB.get("user", id)
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        image = result["image"]
        company = result["company"]                
        partners = len(result["partners"])
        delivery = len(result["delivery"])
        payload = {}
        payload["company"] = company
        payload["partners"] = partners
        payload["delivery"] = delivery
        payload["products"] = 0
        payload["storage"] = len(dB.query("product", {"user": id}, {'_id': False}))
        payload["image"] = image
        return Response(json.dumps(payload),  status=200, mimetype='application/json')


@app.route('/product', methods=['GET', 'POST'])
@auth.login_required
def product():
    body = request.json
    id = body["id"]
    result = dB.query("product", {"user": id}, {'_id': False})
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        return Response(json.dumps(result),  status=200, mimetype='application/json')
        
@app.route('/storage', methods=['GET', 'POST'])
@auth.login_required
def storage():
    body = request.json
    id = body["id"]
    result = dB.query("product", {"user": id}, {'_id': False})
    payload = {}
    payload["products"] = result
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        return Response(json.dumps(payload),  status=200, mimetype='application/json')
        
@app.route('/updateProfilePhoto', methods=['GET', 'POST'])
@auth.login_required
def updateProfilePhoto():
    body = request.json
    id = body["id"]
    image = body["image"]
    try:
        dB.update("user", id, {'image': image})
        return Response(json.dumps({'a':'b'}), status=200, mimetype='application/json')
    except:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        

@app.route('/signup', methods=['GET', 'POST'])
@auth.login_required
def signup():
    body = request.json
    payload = {}

    username = body["username"]
    password = body["password"]
    company = body["company"]
    role = body["role"]
    
    try:
        payload["username"] = username
        payload["password"] = password
        payload["company"] = company
        payload["role"] = role
        payload["count"] = 0
        payload["partners"] = []
        payload["delivery"] = []
        payload["image"] = "https://fhsakaci.s3.fr-par.scw.cloud/images/no-image.png"
        dB.insert("user", payload)
        return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')
    except:
        return Response(json.dumps({'a':'b'}),  status=409, mimetype='application/json')

@app.route('/addProduct', methods=['GET', 'POST'])
@auth.login_required
def addProduct():
    body = request.json
    id = body["id"]
    result = dB.get("user", id)
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        name = body["name"]
        modelNo = body["modelNo"]
        total = body["total"]
        year = body["year"]
        description = body["description"]
        image = body["image"]
        
        payload = {}
        payload["user"] = str(id)
        payload["name"] = name
        payload["modelNo"] = modelNo
        payload["total"] = total
        payload["year"] = year
        payload["image"] = image
        payload["description"] = description
        
        dB.insert("product", payload)
        return Response(status=200, mimetype='application/json')

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

if __name__ == '__main__':
    print('Starting app')
    app.run(host='0.0.0.0', debug=True, port=8080)
