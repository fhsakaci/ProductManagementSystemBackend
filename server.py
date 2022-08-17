from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask import Response
import json
import hashlib
from bson.objectid import ObjectId
import datetime  

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
        deliveryFrom = dB.query("delivery", {"fromId": id})
        deliveryTo = dB.query("delivery", {"toId": id})
        delivery = len(deliveryFrom) + len(deliveryTo)
        payload = {}
        payload["company"] = company
        payload["partners"] = partners
        payload["delivery"] = delivery
        payload["products"] = len(dB.query("product", {"user": id}, {'_id': False})) + delivery
        payload["storage"] = len(dB.query("product", {"user": id}, {'_id': False}))
        payload["image"] = image
        return Response(json.dumps(payload),  status=200, mimetype='application/json')


@app.route('/products', methods=['GET', 'POST'])
@auth.login_required
def products():
    body = request.json
    id = body["id"]
    result = dB.query("product", {"user": id})
    for i in range(len(result)):
        result[i]["id"] = str(result[i].pop("_id"))
    payload = {}
    payload["products"] = result
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        return Response(json.dumps(payload),  status=200, mimetype='application/json')
        
@app.route('/storage', methods=['GET', 'POST'])
@auth.login_required
def storage():
    body = request.json
    id = body["id"]
    result = dB.query("product", {"user": id})
    for i in range(len(result)):
        result[i]["id"] = str(result[i].pop("_id"))
    payload = {}
    payload["products"] = result
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        return Response(json.dumps(payload),  status=200, mimetype='application/json')

@app.route('/partners', methods=['GET', 'POST'])
@auth.login_required
def partners():
    body = request.json
    id = body["id"]
    result = dB.get("user", id)
    if result == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:         
        print(result)      
        partners = result["partners"]
        partnerData = []
        for i in range(len(partners)):
            partner = dB.get("user", partners[i])
            partner["id"] = str(partner.pop("_id"))
            partnerData.append(partner)
        print(partnerData)
        payload = {}
        payload["partners"] = partnerData
        return Response(json.dumps(payload),  status=200, mimetype='application/json')

@app.route('/deliveries', methods=['GET', 'POST'])
@auth.login_required
def deliveries():
    body = request.json
    id = body["id"]
    deliveryFrom = dB.query("delivery", {"fromId": id})
    deliveryTo = dB.query("delivery", {"toId": id})
    deliveryOwner = dB.query("delivery", {"ownerId": id})

    if deliveryFrom == None and deliveryTo == None:
        return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
    else:
        for i in range(len(deliveryFrom)):
            deliveryFrom[i]["_id"] = str(deliveryFrom[i]["_id"])
            product = dB.get("product", str(deliveryFrom[i]["productId"]))
            deliveryFrom[i]["name"] = product["name"]
            deliveryFrom[i]["modelNo"] = product["modelNo"]
            deliveryFrom[i]["image"] = product["image"]
        for i in range(len(deliveryTo)):
            deliveryTo[i]["_id"] = str(deliveryTo[i]["_id"])
            product = dB.get("product", str(deliveryTo[i]["productId"]))
            deliveryTo[i]["name"] = product["name"]
            deliveryTo[i]["modelNo"] = product["modelNo"]
            deliveryTo[i]["image"] = product["image"]
        for i in range(len(deliveryOwner)):
            deliveryOwner[i]["_id"] = str(deliveryOwner[i]["_id"])
            product = dB.get("product", str(deliveryOwner[i]["productId"]))
            deliveryOwner[i]["name"] = product["name"]
            deliveryOwner[i]["modelNo"] = product["modelNo"]
            deliveryOwner[i]["image"] = product["image"]

        payload = {}
        payload["deliveryFrom"] = deliveryFrom
        payload["deliveryTo"] = deliveryTo
        payload["deliveryOwner"] = deliveryOwner
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

    username = body["username"]
    password = body["password"]
    company = body["company"]
    role = body["role"]
    
    try:
        payload = {}
        payload["username"] = username
        payload["password"] = password
        payload["company"] = company
        payload["role"] = role
        payload["count"] = 0
        payload["partners"] = []
        payload["image"] = "https://fhsakaci.s3.fr-par.scw.cloud/images/no-image.png"
        dB.insert("user", payload)
        return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')
    except:
        return Response(json.dumps({'a':'b'}),  status=409, mimetype='application/json')
        

@app.route('/addPartner', methods=['GET', 'POST'])
@auth.login_required
def addPartner():
    body = request.json
    
    adminId = body["id"]
    username = body["username"]
    password = body["password"]
    company = body["company"]
    role = body["role"]

    payload = {}      
    payload["username"] = username
    payload["password"] = password
    payload["company"] = company
    payload["role"] = role
    payload["count"] = 0
    payload["partners"] = []
    payload["image"] = "https://fhsakaci.s3.fr-par.scw.cloud/images/no-image.png"
    result = dB.insert("user", payload)
    partnetId = result
    adminUser = dB.get("user", adminId)
    partners = adminUser["partners"]
    partners.append(partnetId)
    adminUser["partners"] = partners
    dB.update("user", adminId, adminUser)
        
    return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')

@app.route('/addDelivery', methods=['GET', 'POST'])
@auth.login_required
def addDelivery():
    body = request.json
    
    productId = body["productId"]
    ownerId = body["ownerId"]
    fromId = body["fromId"]
    toId = body["toId"]
    piece = body["piece"]
    description = body["description"]

    payload = {}
    payload["productId"] = productId
    payload["ownerId"] = ownerId
    payload["fromId"] = fromId
    payload["toId"] = toId
    payload["piece"] = piece
    payload["description"] = description
    payload["activity"] = True
    payload["creationDate"] = datetime.datetime.now().timestamp()
    payload["lastActivity"] = datetime.datetime.now().timestamp()
    result = dB.insert("delivery", payload)        
    return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')

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
