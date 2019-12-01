"""Holds the database handler to work with mongodb."""
import mongomock as pymongo


class DatabaseHandler:
    """Database handler."""

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["offthedialbot"]

        # Collections
        self.profiles = self.db["profiles"]

    def find_profile(self, id):
        """Find a document in the profiles collection by id."""
        return self.profiles.find_one({"_id": id})

    def new_profile(self, profile, id):
        """Insert a new profile into the profiles collection with id."""
        profile["_id"] = id
        return self.profiles.insert_one(profile)

    def edit_profile(self, profile, id):
        """Update an existing profile in the profiles collection by id."""
        profile["_id"] = id
        return self.profiles.update_one(profile)
