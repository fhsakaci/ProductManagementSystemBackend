from utils import utils


class Delivery:
    databaseName = "Delivery"
    def __init__(self, dB, age):
        self.dB = dB
        self.logger = utils.get_logger()

    def get(self, id, activity = False):
        return self.dB.get(self.databaseName, id)

    def insert(self, payload):
        pass

    def update(self, id, payload):
        pass

    def remove(self, id):
        pass