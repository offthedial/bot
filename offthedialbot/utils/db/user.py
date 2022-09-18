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
            "C-": 650,
            "C": 700,
            "C+": 750,
            "B-": 800,
            "B": 850,
            "B+": 900,
            "A-": 950,
            "A": 1000,
            "A+": 1050,
            "S": 1100,
            "S+0": 1250,
            "S+1": 1340,
            "S+2": 1400,
            "S+3": 1500,
            "S+4": 1575,
            "S+5": 1650,
            "S+6": 1725,
            "S+7": 1800,
            "S+8": 1875,
            "S+9": 1950,
            "S+10": 2000,
            "S+11": 2015,
            "S+12": 2030,
            "S+13": 2045,
            "S+14": 2060,
            "S+15": 2075,
            "S+16": 2090,
            "S+17": 2105,
            "S+18": 2120,
            "S+19": 2135,
            "S+20": 2150,
            "S+21": 2165,
            "S+22": 2180,
            "S+23": 2195,
            "S+24": 2210,
            "S+25": 2225,
            "S+26": 2240,
            "S+27": 2255,
            "S+28": 2270,
            "S+29": 2285,
            "S+30": 2300,
            "S+31": 2315,
            "S+32": 2330,
            "S+33": 2345,
            "S+34": 2360,
            "S+35": 2375,
            "S+36": 2390,
            "S+37": 2405,
            "S+38": 2420,
            "S+39": 2435,
            "S+40": 2450,
            "S+41": 2465,
            "S+42": 2480,
            "S+43": 2495,
            "S+44": 2510,
            "S+45": 2525,
            "S+46": 2540,
            "S+47": 2555,
            "S+48": 2570,
            "S+49": 2585,
            "S+50": 2600,
        }.get(rank, None)
