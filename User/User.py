from utils import utils
from Database.MongoDatabaseConnection import Database

class User:
    databaseName = "User"
    def __init__(self):
        self.dB = Database.getInstance()
        self.logger = utils.get_logger()
    
    def get(self, id):
        return self.dB.get(self.databaseName, id)

    def control(self, username, password):
        return self.dB.SearchUser("user", username, password)

    def insert(self, payload):
        pass

    def update(self, id, payload):
        pass

    def remove(self, id):
        pass
