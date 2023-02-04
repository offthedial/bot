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
        """Get smash.gg data from the api with the user slug."""
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
            elo = statistics.fmean(powers)
            return f"X {str(elo)}"
        return f"{self.dict['profile']['rank']['letter']} {self.dict['profile']['rank']['points']}"

    def get_sortable_rank(self):
        """Convert rank to a sortable version."""
        rank_to_ver = {
            "X": 11_000000,
            "S": 10_000000,
            "A+": 9_000000,
            "A": 8_000000,
            "A-": 7_000000,
            "B+": 6_000000,
            "B": 5_000000,
            "B-": 4_000000,
            "C+": 3_000000,
            "C": 2_000000,
            "C-": 1_000000,
        }
        rank = self.get_rank().split()
        return str(rank_to_ver[rank[0]] + float(rank[1].replace(",", "")))

    def get_weapons(self):
        """Process weapons field."""
        return " // ".join([weapon["name"] for weapon in self.dict["profile"]["weapons"]])
