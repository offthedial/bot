"""Holds the database handler to work with mongodb."""
import mongomock as pymongo


class DatabaseHandler:
    """Database handler."""

    empty_profile = {
        "status": {
            "ign": None,
            "sw": None,
            "rank": {
                "cb": None,
                "rm": None,
                "sz": None,
                "tc": None
            },
        },
        "meta": {
            "competing": False,
        }
    }

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["offthedialbot"]

        # Collections
        self.profiles = self.db["profiles"]
