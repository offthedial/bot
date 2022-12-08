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
            "C-": 600,
            "C": 620,
            "C+": 640,
            "B-": 800,
            "B": 820,
            "B+": 840,
            "A-": 1000,
            "A": 1020,
            "A+": 1040,
            "S": 1200,
            "S+0": 1300,
            "S+1": 1320,
            "S+2": 1340,
            "S+3": 1360,
            "S+4": 1380,
            "S+5": 1400,
            "S+6": 1420,
            "S+7": 1440,
            "S+8": 1460,
            "S+9": 1480,
            "S+10": 1600,
            "S+11": 1620,
            "S+12": 1640,
            "S+13": 1660,
            "S+14": 1680,
            "S+15": 1700,
            "S+16": 1720,
            "S+17": 1740,
            "S+18": 1760,
            "S+19": 1780,
            "S+20": 1800,
            "S+21": 1820,
            "S+22": 1840,
            "S+23": 1860,
            "S+24": 1880,
            "S+25": 1900,
            "S+26": 1920,
            "S+27": 1940,
            "S+28": 1960,
            "S+29": 1980,
            "S+30": 2100,
            "S+31": 2120,
            "S+32": 2140,
            "S+33": 2160,
            "S+34": 2180,
            "S+35": 2200,
            "S+36": 2220,
            "S+37": 2240,
            "S+38": 2260,
            "S+39": 2280,
            "S+40": 2400,
            "S+41": 2420,
            "S+42": 2440,
            "S+43": 2460,
            "S+44": 2480,
            "S+45": 2500,
            "S+46": 2520,
            "S+47": 2540,
            "S+48": 2560,
            "S+49": 2580,
            "S+50": 2600,
        }.get(rank, None)
