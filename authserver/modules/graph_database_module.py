from injector import singleton, Module
from authserver.db.graph_database import AbstractGraphDatabase, Neo4jGraphDatabase


class GraphDatabaseModule(Module):
    def configure(self, binder):
        binder.bind(AbstractGraphDatabase, to=Neo4jGraphDatabase, scope=singleton)
