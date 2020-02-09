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

    # Profiles
    def find_profile(self, id: int):
        """Find a document in the profiles collection by id."""
        return self.profiles.find_one({"_id": id})

    def find_many_profiles(self, query: dict):
        """Find all documents with the given kwargs."""
        return self.profiles.find(query)

    def new_profile(self, profile: dict, id: int):
        """Insert a new profile into the profiles collection with id."""
        profile["_id"] = id
        return self.profiles.insert_one(profile)

    def update_profile(self, profile: dict, id: int):
        """Update an existing profile in the profiles collection by id."""
        profile["_id"] = id
        return self.profiles.replace_one({"_id": id}, profile)

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
