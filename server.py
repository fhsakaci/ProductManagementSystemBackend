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
from FlaskAppWrapper.FlaskAppWrapper import FlaskAppWrapper
from User.User import User
from utils import utils


logger = utils.set_logger( __name__, __file__ )
logger.info('Server service has been started..' )

dB = Database("localhost",27017)
dB.Connect("sakaci","sakaci","product_management_system")

auth = HTTPBasicAuth()
user = 'luiz'
pw = '123'
users = {
    user: generate_password_hash(pw)
}


appp = FlaskAppWrapper(__name__)

if __name__ == '__main__':
    print('Starting app')
    appp.run()
