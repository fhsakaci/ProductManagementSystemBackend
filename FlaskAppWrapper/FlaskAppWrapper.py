import flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Response
from flask import request
import json
import datetime  


from utils import utils
from Database.MongoDatabaseConnection import Database
from User.User import User


auth = HTTPBasicAuth()
user = 'luiz'
pw = '123'
users = {
    user: generate_password_hash(pw)
}
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        answer = self.action()
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = flask.Response(answer, status=200, headers={})
        # Send it
        return self.response

class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = flask.Flask(name)
        self.dB = Database.getInstance()
        self.logger = utils.get_logger()
        self.add_all_endpoints()

    def add_all_endpoints(self):
        # Add root endpoint
        self.add_endpoint(endpoint="/", endpoint_name="/", handler = self.action)

        # Add action endpoints
        
        self.add_endpoint(endpoint="/login", endpoint_name="/login", handler = self.login)
        self.add_endpoint(endpoint="/user", endpoint_name="/user", handler = self.user)
        self.add_endpoint(endpoint="/products", endpoint_name="/products", handler = self.products)
        self.add_endpoint(endpoint="/storage", endpoint_name="/storage", handler = self.storage)
        self.add_endpoint(endpoint="/partners", endpoint_name="/partners", handler = self.partners)
        self.add_endpoint(endpoint="/deliveries", endpoint_name="/deliveries", handler = self.deliveries)
        self.add_endpoint(endpoint="/updateProfilePhoto", endpoint_name="/updateProfilePhoto", handler = self.updateProfilePhoto)
        self.add_endpoint(endpoint="/signup", endpoint_name="/signup", handler = self.signup)
        self.add_endpoint(endpoint="/addPartner", endpoint_name="/addPartner", handler = self.addPartner)
        self.add_endpoint(endpoint="/addDelivery", endpoint_name="/addDelivery", handler = self.addDelivery)
        self.add_endpoint(endpoint="/addProduct", endpoint_name="/addProduct", handler = self.addProduct)
        self.add_endpoint(endpoint="/finishDelivery", endpoint_name="/finishDelivery", handler = self.finishDelivery)
        # you can add more ... 

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        decorator = self.app.route(endpoint, methods=['GET', 'POST'])
        decoratorHandler = decorator(handler)
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(decoratorHandler)) 
        # You can also add options here : "... , methods=['POST'], ... "

    
    def run(self):
        self.app.run(host='0.0.0.0', debug=True, port=8080,)

    # ==================== ------ API Calls ------- ====================
    def action(self):
        # Dummy action
        return "action" # String that will be returned and display on the webpage
        # Test it with curl 127.0.0.1:5000

    def add_X(self):
        # Dummy action
        return "add_X"
        # Test it with curl 127.0.0.1:5000/add_X

    def login(self):
        print(request)
        payload = request.json
        username = payload["username"]
        password = payload["password"]
        us = User()
        result = us.control(username, password)
        if result == False:
            return Response(status=401, mimetype='application/json')
        else:
            return Response(json.dumps({'id':str(result["_id"])}),  status=200, mimetype='application/json')

    def user(self):
        body = request.json
        id = body["id"]
        result = self.dB.get("user", id)
        if result == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            image = result["image"]
            role = result["role"]
            company = result["company"]                
            partners = len(result["partners"])
            deliveryFrom = self.dB.query("delivery", {"fromId": id, "activity": True })
            deliveryTo = self.dB.query("delivery", {"toId": id, "activity": True})
            delivery = len(deliveryFrom) + len(deliveryTo)
            payload = {}
            payload["company"] = company
            payload["partners"] = partners
            payload["delivery"] = delivery
            payload["role"] = role
            payload["products"] = len(self.dB.query("product", {"user": id}, {'_id': False})) + delivery
            payload["storage"] = len(self.dB.query("product", {"user": id}, {'_id': False}))
            payload["image"] = image
            return Response(json.dumps(payload),  status=200, mimetype='application/json')

    def products(self):
        body = request.json
        id = body["id"]
        result = self.dB.query("product", {"user": id})
        for i in range(len(result)):
            result[i]["id"] = str(result[i].pop("_id"))
            result[i]["piece"] = self.dB.query("storage", {"productId": result[i]["id"]})[0]["piece"]
        payload = {}
        payload["products"] = result
        if result == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            return Response(json.dumps(payload),  status=200, mimetype='application/json')
            
    def storage(self):
        body = request.json
        id = body["id"]
        result = self.dB.query("storage", {"userId": id})
        if result == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            products = []
            for i in range(len(result)):
                product = self.dB.get("product", (result[i]["productId"]))
                product["id"] = str(product.pop("_id"))
                product["piece"] = result[i]["piece"]
                products.append(product)

            payload = {}
            payload["products"] = products
            return Response(json.dumps(payload),  status=200, mimetype='application/json')

    def partners(self):
        body = request.json
        id = body["id"]
        result = self.dB.get("user", id)
        if result == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            if result["role"] == "admin":
                partners = result["partners"]
                partnerData = []
                for i in range(len(partners)):
                    partner = self.dB.get("user", partners[i])
                    partner["id"] = str(partner.pop("_id"))
                    partnerData.append(partner)
                payload = {}
                payload["partners"] = partnerData
                return Response(json.dumps(payload),  status=200, mimetype='application/json')
            else:
                adminId = result["adminId"]
                adminUser = self.dB.get("user", adminId)
                adminUser["id"] = str(adminUser.pop("_id"))
                adminUser.pop("password")
                partners = adminUser.pop("partners")

                partnerData = []
                partnerData.append(adminUser)
                for i in range(len(partners)):
                    partner = self.dB.get("user", partners[i])
                    partner["id"] = str(partner.pop("_id"))
                    if partner["id"] != id:
                        partnerData.append(partner)
                payload = {}
                payload["partners"] = partnerData
                print(partnerData)
                return Response(json.dumps(payload),  status=200, mimetype='application/json')
                
    def deliveries(self):
        body = request.json
        id = body["id"]
        deliveryFrom = self.dB.query("delivery", {"fromId": id, "activity": True})
        deliveryTo = self.dB.query("delivery", {"toId": id, "activity": True})
        deliveryOwner = self.dB.query("delivery", {"ownerId": id})

        if deliveryFrom == None and deliveryTo == None and deliveryOwner == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            for i in range(len(deliveryFrom)):
                deliveryFrom[i]["_id"] = str(deliveryFrom[i]["_id"])
                product = self.dB.get("product", str(deliveryFrom[i]["productId"]))
                deliveryFrom[i]["name"] = product["name"]
                deliveryFrom[i]["modelNo"] = product["modelNo"]
                deliveryFrom[i]["image"] = product["image"]
            for i in range(len(deliveryTo)):
                deliveryTo[i]["_id"] = str(deliveryTo[i]["_id"])
                product = self.dB.get("product", str(deliveryTo[i]["productId"]))
                deliveryTo[i]["name"] = product["name"]
                deliveryTo[i]["modelNo"] = product["modelNo"]
                deliveryTo[i]["image"] = product["image"]
            for i in range(len(deliveryOwner)):
                deliveryOwner[i]["_id"] = str(deliveryOwner[i]["_id"])
                product = self.dB.get("product", str(deliveryOwner[i]["productId"]))
                deliveryOwner[i]["name"] = product["name"]
                deliveryOwner[i]["modelNo"] = product["modelNo"]
                deliveryOwner[i]["image"] = product["image"]

            payload = {}
            payload["deliveryFrom"] = deliveryFrom
            payload["deliveryTo"] = deliveryTo
            payload["deliveryOwner"] = deliveryOwner
            return Response(json.dumps(payload),  status=200, mimetype='application/json')
            
    def updateProfilePhoto(self):
        body = request.json
        id = body["id"]
        image = body["image"]
        try:
            self.dB.update("user", id, {'image': image})
            return Response(json.dumps({'a':'b'}), status=200, mimetype='application/json')
        except:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
            

    def signup(self):
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
            self.dB.insert("user", payload)
            return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')
        except:
            return Response(json.dumps({'a':'b'}),  status=409, mimetype='application/json')
            

    def addPartner(self):
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
        payload["adminId"] = adminId
        payload["count"] = 0
        payload["partners"] = []
        payload["image"] = "https://fhsakaci.s3.fr-par.scw.cloud/images/no-image.png"
        result = self.dB.insert("user", payload)
        partnetId = result
        adminUser = self.dB.get("user", adminId)
        partners = adminUser["partners"]
        partners.append(partnetId)
        adminUser["partners"] = partners
        self.dB.update("user", adminId, adminUser)
            
        return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')

    def addDelivery(self):
        body = request.json
        
        productId = body["productId"]
        product = self.dB.get("product", productId)
        ownerId = product["user"]
        fromId = body["fromId"]
        toId = body["toId"]
        piece = int(body["piece"])
        description = body["description"]

        storageProduct = self.dB.query("storage", {"productId":productId, "userId": fromId})[0]
        totalPiece = int(storageProduct["piece"]) - int(piece)
        self.dB.update("storage", storageProduct["_id"], {"piece": totalPiece})

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
        result = self.dB.insert("delivery", payload)        
        return Response(json.dumps({'a':'b'}),  status=200, mimetype='application/json')

    def addProduct(self):
        body = request.json
        id = body["id"]
        result = self.dB.get("user", id)
        if result == None:
            return Response(json.dumps({'a':'b'}), status=401, mimetype='application/json')
        else:
            name = body["name"]
            modelNo = body["modelNo"]
            piece = int(body["piece"])
            year = body["year"]
            description = body["description"]
            image = body["image"]
            
            payload = {}
            payload["user"] = str(id)
            payload["name"] = name
            payload["modelNo"] = modelNo
            payload["year"] = year
            payload["image"] = image
            payload["description"] = description
            productId = self.dB.insert("product", payload)

            payload = {}
            payload["userId"] = str(id)
            payload["productId"] = str(productId)
            payload["piece"] = piece
            self.dB.insert("storage", payload)
            return Response(status=200, mimetype='application/json')


    def finishDelivery(self):
        body = request.json
        userId = body["userId"]
        deliveryId = body["deliveryId"]
        piece = int(body["piece"])
        description = body["description"]

        delivery = self.dB.get("delivery", deliveryId)
        productId = delivery["productId"]
        deliveryOwner = delivery["ownerId"]
        
        
        deliveryProduct = self.dB.query("storage", {"productId": productId, "userId": userId})
        if deliveryProduct == []:
            payload = {}
            payload["userId"] = str(userId)
            payload["productId"] = str(productId)
            payload["piece"] = piece
            self.dB.insert("storage", payload)
            self.dB.update("delivery", deliveryId, {"activity": False})
            if int(delivery["piece"]) - piece != 0:
                delivery.pop("_id")
                delivery["piece"] = int(delivery["piece"]) - piece
                self.dB.insert("delivery", delivery)
            return Response(status=200, mimetype='application/json')
        else:
            deliveryProduct = deliveryProduct[0]
            self.dB.update("storage", str(deliveryProduct["_id"]), {"piece": int(deliveryProduct["piece"]) + piece})
            self.dB.update("delivery", deliveryId, {"activity": False})
            if int(delivery["piece"]) - piece != 0:
                delivery.pop("_id")
                delivery["piece"] = int(delivery["piece"]) - piece
                self.dB.insert("delivery", delivery)
            return Response(status=200, mimetype='application/json')


