"""Contains tools to help with managing times."""
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from offthedialbot import utils


class User:
    """Tools for dealing with users and times."""

    symbols = """
    - years: `y/Y`, `yr(s)`, `year(s)`
    - months: `m`, `mon(s)`, `month(s)`
    - weeks: `w/W`, `week(s)`
    - days: `d/D`, `day(s)`
    - hours: `h/H`, `hr(s)`, `hour(s)`
    - minutes: `M`, `min(s)`, `minute(s)`
    - seconds: `s/S`, `sec(s)`, `second(s)`
    
    Units must be provided in descending order of magnitude.
    """

    complied = re.compile(
        r"((?P<years>\d+?) ?(years|year|yrs|yr|Y|y) ?)?"
        r"((?P<months>\d+?) ?(months|month|mons|mon|m) ?)?"
        r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
        r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
        r"((?P<hours>\d+?) ?(hours|hour|hrs|hr|H|h) ?)?"
        r"((?P<minutes>\d+?) ?(minutes|minute|mins|min|M) ?)?"
        r"((?P<seconds>\d+?) ?(seconds|second|secs|sec|S|s))?"
    )

    @classmethod
    def parse(cls, duration: str):
        """Convert user-inputted times to datetime objects, (3d, 5M, 2y)."""
        match = cls.complied.fullmatch(duration)
        if not match:
            return False

        delta = relativedelta(**{unit: int(amount) for unit, amount in match.groupdict(default=0).items()})
        now = datetime.utcnow()
        return now + delta


class Timer:
    """Tools for dealing with timers."""

    timers = utils.dbh.timers

    @classmethod
    def schedule(cls, when: datetime, /, destination: int, author: int, *, style, title: str, description: str):
        """ Schedule a [coro]utine at [when], and return timer id.

        :param datetime when: Datetime object for when to send the alert
        :param int destination: Discord channel/user id. Channel ID to send to a channel and user ID to send a DM.
        :param int author: User ID of the timer author.
        :param style: Alert style.
        :param title: Alert title.
        :param description: Alert description.
        """
        timer = cls.timers.insert_one({
            "when": when,
            "destination": destination,
            "author": author,
            "alert": {
                "style": style,
                "title": title,
                "description": description
            }})
        return timer.inserted_id

    @classmethod
    def delete(cls, timer_id=None, /, **kwargs):
        """Delete a timer given their id."""
        if timer_id:  kwargs["_id"] = timer_id
        return cls.timers.delete_one(kwargs)

    @classmethod
    def get(cls, query=None):
        if query is None:
            query = {}
        if "timers" not in utils.dbh.db.list_collection_names():
            return []
        return utils.dbh.timers.find(query)
