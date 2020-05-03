"""Contains the DatabaseHandler class."""

from offthedialbot import logger, env

if env.get("debug"):
    from mongomock import MongoClient
else:
    from pymongo import MongoClient


class DatabaseHandler:
    """Custom database handler that works with mongodb."""

    def __init__(self):
        self.client = MongoClient("mongodb://mongo:27017/")
        logger.debug("New MongoClient has been created (port:27017).")
        self.db = self.client["offthedialbot"]

        # Collections
        self.profiles = self.db["profiles"]
        self.metaprofiles = self.db["metaprofiles"]
        self.to = self.db["to"]
        self.timers = self.db["timers"]


dbh = DatabaseHandler()
