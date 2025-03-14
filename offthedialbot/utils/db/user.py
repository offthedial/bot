import statistics
import discord
from offthedialbot import utils
from firebase_admin import firestore
from . import db, Tournament
from .signup import Signup


class User:
    """Represents what useUser would be."""

    col = db.collection(u"users")

    def __init__(self, id):
        self.id = str(id)
        self.doc = self.col.document(self.id).get()
        self.ref = self.doc.reference
        self.dict = self.doc.to_dict()
        self.tourney = Tournament()

    def signup(self, ignore_ended=False):
        """Return the possible user's signup (useSignup)."""
        if self.tourney.has_ended() and not ignore_ended:
            return None

        try:
            return Signup(self.id, self, self.tourney)
        except LookupError:
            return None

    async def smashgg(self):
        """Get start.gg data from the api with the user slug."""
        query = """query($slug: String) {
          user(slug: $slug) {
            player {
              gamerTag
            }
          }
        }"""
        status, data = await utils.graphql("smashgg", query, {"slug": self.dict["profile"]["slug"]})
        return data["data"]["user"]

    def discord(self, context):
        if isinstance(context, discord.Client):
            return context.get_user(int(self.id))
        if isinstance(context, discord.Guild):
            return context.get_member(int(self.id))

    def increment_ss(self, by: int):
        """Increment signal strength by an amount."""
        return self.ref.update({"meta.signal": firestore.Increment(by)})

    def get_rank(self):
        """Get string representation of rank."""
        if self.dict["profile"]["isUnlocked"] == "yes":
            powers = []
            for rank in ["sz", "tc", "rm", "cb"]:
                if p := self.dict["profile"]["rank"].get(rank, False):
                    powers.append(float(p))
            elo = round(statistics.fmean(powers), 1)
            return f"X {str(elo)} (max: {str(max(powers))})"
        return f"{self.dict['profile']['rank']['letter']} {self.dict['profile']['rank']['points']}"

    def get_sortable_rank(self):
        """Convert rank to a sortable version."""
        rank_to_ver = {
            "X": 21_0000,
            "S": 19_0000,
            "A+": 17_0000,
            "A": 15_0000,
            "A-": 13_0000,
            "B+": 11_0000,
            "B": 9_0000,
            "B-": 7_0000,
            "C+": 5_0000,
            "C": 3_0000,
            "C-": 1_0000,
        }
        rank = self.get_rank().split()
        return str(rank_to_ver[rank[0]] + float(rank[1].replace(",", "")))

    def get_weapons(self):
        """Process weapons field."""
        return " // ".join([weapon["name"] for weapon in self.dict["profile"]["weapons"]])
