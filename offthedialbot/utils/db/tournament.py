from firebase_admin.firestore import Query
from datetime import datetime

from offthedialbot.utils import smashgg
from . import db


class Tournament:
    """Represents what useTournament would be."""

    col = db.collection(u'tournaments')

    @classmethod
    async def new_tourney(cls, *, type, slug):
        tourney = {
            "date": datetime.utcnow(),
            "type": type,
            "slug": slug,
            "smashgg": await cls.query_smashgg(slug)
        }
        cls.col.add(tourney)
        return cls()

    def __init__(self):
        self.doc = next(iter(self.col.order_by(u"date", direction=Query.DESCENDING).limit(1).stream()))
        self.dict = self.doc.to_dict()

    def signups(self, col=False, ignore_ended=False):
        """Return a stream of tournament signups."""
        if self.has_ended() and not ignore_ended:
            return None

        signups = self.doc.reference.collection(u'signups')
        return signups if col else signups.stream()

    def subs(self, col=False, ignore_ended=False):
        """Return a stream of tournament subs."""
        if self.has_ended() and not ignore_ended:
            return None

        subs = self.doc.reference.collection(u'subs')
        return subs if col else subs.stream()

    def has_ended(self):
        """Returns whether the tournament has ended."""
        return datetime.utcfromtimestamp(self.dict["smashgg"]["endAt"]) < datetime.utcnow()

    def is_reg_open(self):
        """Returns whether the tournament registration is open."""
        return datetime.utcfromtimestamp(self.dict["smashgg"]["registrationClosesAt"]) > datetime.utcnow()

    async def sync_smashgg(self):
        smashgg = await self.query_smashgg(self.dict["slug"])
        self.doc.update({"smashgg": smashgg})
        self.dict["smashgg"] = smashgg  # Optimistic update

    @staticmethod
    async def query_smashgg(slug):
        """Query the smash.gg graphql api."""
        query = """query($slug: String) {
          tournament(slug: $slug){
            name
            registrationClosesAt
            endAt
          }
        }"""
        status, resp = await smashgg.post(query, {"slug": slug})
        return resp["data"]["tournament"]
