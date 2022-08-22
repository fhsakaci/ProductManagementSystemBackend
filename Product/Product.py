from utils import utils


class Product:
    databaseName = "Product"
    def __init__(self, dB, age):
        self.dB = dB
        self.logger = utils.get_logger()

    def get(self, id):
        pass

    def insert(self, payload):
        return self.dB.get(self.databaseName, id)

    def update(self, id, payload):
        pass

    def remove(self, id):
        pass
