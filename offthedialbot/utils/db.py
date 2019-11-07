"""Holds the database handler to work with mongodb."""
import mongomock as pymongo


class DatabaseHandler:
    """Database handler."""

    empty_profile = {
        "status": {
            "IGN": None,
            "SW": None,
            "Ranks": {
                "Splat Zones": None,
                "Rainmaker": None,
                "Tower Control": None,
                "Clam Blitz": None,
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
