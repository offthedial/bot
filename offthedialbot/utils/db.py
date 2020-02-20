"""Contains the DatabaseHandler class."""
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("DEBUG"):
    import mongomock as pymongo
else:
    import pymongo


class DatabaseHandler:
    """Custom database handler that works with mongodb."""

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["offthedialbot"]

        # Collections
        self.profiles = self.db["profiles"]
        self.links = self.db["links"]

    # Links
    def set_tourney_link(self, link):
        """Set the tournament link."""
        link = {"_id": "tourney", "link": link}
        return self.links.replace_one({"_id": "tourney"}, link, upsert=True)

    def get_tourney_link(self):
        """Get the tournament link."""
        link = self.links.find_one({"_id": "tourney"})
        if link:
            return link["link"]


dbh = DatabaseHandler()
