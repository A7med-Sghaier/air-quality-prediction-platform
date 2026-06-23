from pymongo import MongoClient
import air_pollution.config.mongodb_config as cnf


class MongoDbAdapter:
    instance = None
    client = None
    database = None

    @staticmethod
    def get_instance():
        if MongoDbAdapter.instance is None:
            MongoDbAdapter.instance = MongoDbAdapter(database=cnf.mongodb_config['database'],
                                                     uri=cnf.mongodb_config['uri'])

        return MongoDbAdapter.instance

    def __init__(self, database, uri):
        self.client = self.get_mongodb_connection(uri=uri)
        self.database = self.get_database(database_name=database)

    def get_mongodb_connection(self, uri):
        return MongoClient(uri)

    def get_database(self, database_name):
        return self.client[database_name]

    def get_collection(self, collection_name):
        return self.database.get_collection(collection_name)
