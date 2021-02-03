from flask import g
from abc import ABC, abstractmethod
from injector import inject
from neo4j import GraphDatabase, basic_auth, Transaction
from authserver.config import AbstractConfiguration


class AbstractGraphDatabase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        """Establish a connection to the Graph database."""
        pass

    @abstractmethod
    def query(self, query: str):
        """Execute a query on the Graph database.
        Args:
            query (str): The query to execute.
        Returns:
            obj: The query result.
        """
        pass

    @abstractmethod
    def close(self):
        """Closes the database connection."""
        pass


class Neo4jGraphDatabase(AbstractGraphDatabase):
    @inject
    def __init__(self, config: AbstractConfiguration):
        self._config = config
        self._driver = None

    def connect(self):
        """Establish a connection to the Graph database."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(uri=self._config.connection_uri,
                                                auth=basic_auth(self._config.graph_db_user, self._config.graph_db_password),
                                                encrypted=self._config.graph_db_encrypted)

        if not hasattr(g, 'graph_db'):
            g.graph_db = self._driver.session()
        return g.graph_db

    def query(self, query: str, params: dict = None, transaction: Transaction = None):
        """Execute a query on the Graph database.
        Args:
            query (str): The query to execute.
        Returns:
            obj: The query result.
        """

        if transaction:
            results = transaction.run(query, params)
        else:
            db = self.connect()
            results = db.run(query, params)

        return results

    def close(self):
        """Closes the database connection."""
        if hasattr(g, 'graph_db'):
            g.graph_db.close()
