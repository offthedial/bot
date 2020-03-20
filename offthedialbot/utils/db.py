"""Contains the DatabaseHandler class."""

from offthedialbot import env

if env.get("debug"):
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
        self.to = self.db["to"]
        self.timers = self.db["timers"]

    def new_tourney(self, link: str, rules: str, reg: bool = True):
        return self.to.insert_one({
            "_id": 0,
            "link": link,
            "rules": rules,
            "reg": reg
        })

    def get_tourney(self):
        return self.to.find_one({"_id": 0})

    def end_tourney(self):
        return self.to.find_one_and_delete({"_id": 0})

    def set_tourney_reg(self, reg):
        return self.to.update_one({"_id": 0}, {"$set": {"reg": reg}})


dbh = DatabaseHandler()
