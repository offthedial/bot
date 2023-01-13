from firebase_admin.firestore import Query
from datetime import datetime

from offthedialbot import utils
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
        self.ref = self.doc.reference
        self.dict = self.doc.to_dict()

    def signups(self, col=False, ignore_ended=False):
        """Return a stream of tournament signups."""
        if self.has_ended() and not (ignore_ended or col):
            return None

        signups = self.ref.collection(u'signups')
        return signups if col else signups.stream()

    def subs(self, col=False, ignore_ended=False):
        """Return a stream of tournament subs."""
        if self.has_ended() and not (ignore_ended or col):
            return None

        subs = self.ref.collection(u'subs')
        return subs if col else subs.stream()

    def status(self):
        """Return the current status of the tournament."""
        if self.has_ended():
            return "> ℹ️ `Tournament has ended.`"
        if self.has_reg_closed():
            return "> ⚠️ `Registration has closed.`"
        return "> ✅ `Registration is open!`"

    def has_ended(self):
        """Returns whether the tournament has ended."""
        return self.dict["smashgg"]["endAt"] < datetime.utcnow().timestamp()

    def has_reg_closed(self):
        """Returns whether the tournament registration is open."""
        return self.dict["smashgg"]["registrationClosesAt"] < datetime.utcnow().timestamp()

    def ends_at(self):
        return datetime.utcfromtimestamp(self.dict["smashgg"]["endAt"]).strftime('%a, %b %d at %I:%M %p UTC')

    def reg_closes_at(self):
        return datetime.utcfromtimestamp(self.dict["smashgg"]["registrationClosesAt"]).strftime('%a, %b %d at %I:%M %p UTC')

    def date(self):
        return self.dict["date"].strftime('%a, %b %d at %I:%M %p UTC')

    async def sync_smashgg(self):
        smashgg = await self.query_smashgg(self.dict["slug"])
        self.ref.update({"smashgg": smashgg})
        self.dict["smashgg"] = smashgg  # Optimistic update

    @staticmethod
    async def query_smashgg(slug, q=None):
        """Query the smash.gg graphql api."""
        q = q if q else """
            name
            endAt
            startAt
            registrationClosesAt
        """
        query = f"""query($slug: String) {{
          tournament(slug: $slug) {{
            {q}
          }}
        }}
        """

        status, resp = await utils.graphql("smashgg", query, {"slug": slug})
        return resp["data"]["tournament"]
