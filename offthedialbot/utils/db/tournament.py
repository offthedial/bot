from firebase_admin.firestore import Query
from datetime import datetime, timedelta

from offthedialbot import utils
from . import db


REGISTRATION_CLOSES_BEFORE = timedelta(hours=72)
TOURNAMENT_LASTS = timedelta(hours=24)


class Tournament:
    """Represents what useTournament would be."""

    col = db.collection(u'tournaments')

    @classmethod
    async def new_tourney(cls, *, type, sendou_id):
        tourney = {
            "date": datetime.utcnow(),
            "type": type,
            "sendouId": sendou_id,
            "sendou": await cls.query_sendou(sendou_id)
        }
        cls.col.add(tourney)
        return cls()

    def __init__(self):
        self.doc = next(iter(self.col.order_by(u"date", direction=Query.DESCENDING).limit(1).stream()))
        self.ref = self.doc.reference
        self.dict = self.doc.to_dict()
        self.sendou_link = f"[sendou.ink]({self.dict['sendou']['url']})"

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
        starts = datetime.utcfromtimestamp(self.dict["sendou"]["startAt"])
        return starts + TOURNAMENT_LASTS < datetime.utcnow()

    def has_reg_closed(self):
        """Returns whether the tournament registration is closed."""
        starts = datetime.utcfromtimestamp(self.dict["sendou"]["startAt"])
        return starts - REGISTRATION_CLOSES_BEFORE < datetime.utcnow()

    def ends_at(self):
        starts = datetime.utcfromtimestamp(self.dict["sendou"]["startAt"])
        return (starts + TOURNAMENT_LASTS).strftime('%a, %b %d at %I:%M %p UTC')

    def reg_closes_at(self):
        starts = datetime.utcfromtimestamp(self.dict["sendou"]["startAt"])
        return (starts - REGISTRATION_CLOSES_BEFORE).strftime('%a, %b %d at %I:%M %p UTC')

    def starts_at(self):
        return datetime.utcfromtimestamp(self.dict["sendou"]["startAt"]).strftime('%a, %b %d at %I:%M %p UTC')

    def date(self):
        return self.dict["date"].strftime('%a, %b %d at %I:%M %p UTC')

    def brackets(self):
        """Return the tournament's brackets, in the order sendou.ink indexes them."""
        return self.dict["sendou"]["brackets"]

    async def sync_sendou(self):
        sendou = await self.query_sendou(self.dict["sendouId"])
        self.ref.update({"sendou": sendou})
        self.dict["sendou"] = sendou  # Optimistic update

    @staticmethod
    async def query_sendou(id, ctx=None):
        """Query the sendou.ink api, flattened into the shape stored in firestore."""
        data = await utils.sendou.tournament(id, ctx=ctx)
        return {
            "name": data["name"],
            "url": data["url"],
            "logoUrl": data["logoUrl"],
            "startAt": int(datetime.fromisoformat(
                data["startTime"].replace("Z", "+00:00")).timestamp()),
            "registeredCount": data["teams"]["registeredCount"],
            "checkedInCount": data["teams"]["checkedInCount"],
            "brackets": data["brackets"],
            "isFinalized": data["isFinalized"],
        }
