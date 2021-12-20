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

    def increment_ss(self, by: int):
        """Increment signal strength by an amount."""
        return self.ref.update({"meta.signal": firestore.Increment(by)})

    async def smashgg(self):
        """Get smash.gg data from the api with the user slug."""
        query = """query($slug: String) {
          user(slug: $slug) {
            player {
              gamerTag
            }
          }
        }"""
        status, data = await utils.graphql("smashgg", query, {"slug": self.dict["profile"]["smashgg"][-8:]})
        return data["data"]["user"]

    def discord(self, context):
        if isinstance(context, discord.Client):
            return context.get_user(int(self.id))
        if isinstance(context, discord.Guild):
            return context.get_member(int(self.id))

    async def fetch_discord(self, client):
        return await client.fetch_user(int(self.id))

    def get_elo(self):
        return self.rank_to_power(self.dict["profile"]["rank"])

    @staticmethod
    def rank_to_power(rank):
        if rank.startswith("X"):
            return float(rank[1:])
        return {
            "C-": 1000,
            "C": 1100,
            "C+": 1200,
            "B-": 1250,
            "B": 1450,
            "B+": 1550,
            "A-": 1650,
            "A": 1700,
            "A+": 1800,
            "S": 1900,
            "S+0": 2000,
            "S+1": 2080,
            "S+2": 2120,
            "S+3": 2160,
            "S+4": 2200,
            "S+5": 2230,
            "S+6": 2260,
            "S+7": 2290,
            "S+8": 2320,
            "S+9": 2350,
        }.get(rank, None)
