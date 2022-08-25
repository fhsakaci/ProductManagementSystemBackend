import pymongo
from bson.objectid import ObjectId
from utils import utils

class Database():
    __instance = None

    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Database.__instance == None:
            Database()
        return Database.__instance


    def __init__(self,host,port):
        if Database.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.host=host
            self.port=port
            Database.__instance = self
        
        
    def Connect(self,username,password,DBname):
        self.username=username
        self.password=password
        self.DBname=DBname

        client = pymongo.MongoClient(self.host,self.port)
        mongoDB = client[self.DBname]
        #mongoDB.authenticate(self.username, self.password)
        self.mongoDB=mongoDB

        self.logger = utils.get_logger()

    def insert(self,collection,payload):
        mycol=self.mongoDB[collection]
        self.logger.info("Data send to "+collection+" Collection in MongoDB")
        return mycol.insert(payload)
        

    def save(self,collection,payload):
        mycol=self.mongoDB[collection]
        mycol.save(payload)
        self.logger.info("Data save to "+collection+" Collection in MongoDB")

    def remove_row(self,collection,id):
        mycol=self.mongoDB[collection]
        attribute_filter={"_id":ObjectId(id)}
        mycol.delete_one(attribute_filter)
        
    def update(self,collection,id,data):
        filter={"_id": ObjectId(id)}
        mycol=self.mongoDB[collection]
        mycol.update_one(filter,{"$set":data},upsert=True)

    def query(self,collection,filter,field_filter=None):
        mycol=self.mongoDB[collection]
        results=list(mycol.find(filter,field_filter))
        return results
    
    def get(self,collection,id):
        mycol = self.mongoDB[collection]
        return mycol.find_one({"_id":ObjectId(id)})

    def Query(self,collection,search,ID):
        myquery = {str(search):ID}
        mycol=self.mongoDB[collection]
        results=list(mycol.find(myquery))
        return results
    
    def GetAllData(self,collection):
        mycol=self.mongoDB[collection]
        return list(mycol.find())

    def SearchUser(self,collection,username,password):
        myquery = {str("username"):username,str("password"):password}
        mycol = self.mongoDB[collection]
        results = list(mycol.find(myquery))
        if results == []:
            return False
        else:
            return results[0]

    def SeachCustomerDevice(self,collection,customerId):
        myquery = {'customerId':ObjectId(str(customerId))}
        mycol=self.mongoDB[collection]
        results=list(mycol.find(myquery))
        return results

    def GetLastNumData(self,collection,search,attribute_filter,ID,num):
        myquery = {str(search):ID}
        mycol=self.mongoDB[collection]
        results=list(mycol.find(myquery,attribute_filter,sort=[( '_id', pymongo.DESCENDING )],limit=num))
        return results

    def GetBetween2Date(self,collection,search,attribute_filter,ID,first_date,last_date):
        myquery = {'timestamp':{'$gte':first_date,'$lte':last_date},"sensor._id":ID}
        mycol=self.mongoDB[collection]
        results=list(mycol.find(myquery,attribute_filter))
        return results
    
    def deleteLastData(self,collection,attribute_filter,field_attribute_filter=None):
        try:
            mycol = self.mongoDB[collection]
            results=list(mycol.find(attribute_filter,field_attribute_filter))
            delete_row={"_id":ObjectId(results[0]["_id"])}
            mycol.delete_one(delete_row)
            return results
        except Exception as e:
            self.logger.error("Error '{0}' occurred.".format(e))
    
    def get_with_name_with_attribute(self,collection,payload):
        mycol=self.mongoDB[collection]
        return mycol.find_one(payload)

    def __main__(self):
        pass
