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

    @classmethod
    def display(cls, timestamp: int, format: str) -> str:
        """Return a string that displays a time based on a timestamp."""
        return datetime.utcfromtimestamp(timestamp).strftime(format)

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


class Zone:

    tz_offsets = {
        'A': 0,
        'ACDT': 630,
        'ACST': 570,
        'ACT': -300,
        'ADT': -180,
        'AEDT': 660,
        'AEST': 600,
        'AFT': 270,
        'AKDT': -480,
        'AKST': -540,
        'AMST': -180,
        'AMT': -240,
        'ART': -180,
        'AST': -240,
        'AWDT': 540,
        'AWST': 480,
        'AZOST': -60,
        'AZT': 240,
        'B': 120,
        'BDT': 480,
        'BIOT': 360,
        'BIT': -720,
        'BOT': -240,
        'BRST': -120,
        'BRT': -180,
        'BST': 60,
        'BTT': 360,
        'C': 180,
        'CAT': 120,
        'CCT': 390,
        'CDT': -300,
        'CEDT': 120,
        'CEST': 120,
        'CET': 60,
        'CHADT': 825,
        'CHAST': 765,
        'CHOT': 480,
        'CHUT': 600,
        'CIST': -480,
        'CIT': 480,
        'CKT': -600,
        'CLST': -180,
        'CLT': -240,
        'COST': -240,
        'COT': -300,
        'CST': -360,
        'CT': 480,
        'CVT': -60,
        'CWST': 525,
        'CXT': 420,
        'ChST': 600,
        'D': 240,
        'DAVT': 420,
        'DDUT': 600,
        'DFT': 60,
        'E': 300,
        'EASST': -300,
        'EAST': -360,
        'EAT': 180,
        'ECT': -300,
        'EDT': -240,
        'EEDT': 180,
        'EEST': 180,
        'EET': 120,
        'EGST': 0,
        'EGT': -60,
        'EIT': 540,
        'EST': -300,
        'F': 360,
        'FET': 180,
        'FJT': 720,
        'FKST': -180,
        'FKT': -240,
        'FNT': -120,
        'G': 420,
        'GALT': -360,
        'GAMT': -540,
        'GET': 240,
        'GFT': -180,
        'GILT': 720,
        'GIT': -540,
        'GMT': 0,
        'GST': -120,
        'GYT': -240,
        'H': 480,
        'HADT': -540,
        'HAEC': 120,
        'HAST': -600,
        'HKT': 480,
        'HMT': 300,
        'HOVT': 420,
        'HST': -600,
        'I': 540,
        'ICT': 420,
        'IDT': 180,
        'IOT': 180,
        'IRDT': 270,
        'IRKT': 480,
        'IRST': 210,
        'IST': 330,
        'JST': 540,
        'K': 600,
        'KGT': 360,
        'KOST': 660,
        'KRAT': 420,
        'KST': 540,
        'L': 660,
        'LHST': 630,
        'LINT': 840,
        'M': 720,
        'MAGT': 720,
        'MART': -510,
        'MAWT': 300,
        'MDT': -360,
        'MEST': 120,
        'MET': 60,
        'MHT': 720,
        'MIST': 660,
        'MIT': -510,
        'MMT': 390,
        'MSK': 180,
        'MST': -420,
        'MUT': 240,
        'MVT': 300,
        'MYT': 480,
        'N': -60,
        'NCT': 660,
        'NDT': -90,
        'NFT': 690,
        'NPT': 345,
        'NST': -150,
        'NT': -150,
        'NUT': -660,
        'NZDT': 780,
        'NZST': 720,
        'O': -120,
        'OMST': 360,
        'ORAT': 300,
        'P': -180,
        'PDT': -420,
        'PET': -300,
        'PETT': 720,
        'PGT': 600,
        'PHOT': 780,
        'PKT': 300,
        'PMDT': -120,
        'PMST': -180,
        'PONT': 660,
        'PST': -480,
        'PYST': -180,
        'PYT': -240,
        'R': -300,
        'RET': 240,
        'ROTT': -180,
        'S': -360,
        'SAMT': 240,
        'SAST': 120,
        'SBT': 660,
        'SCT': 240,
        'SGT': 480,
        'SLST': 330,
        'SRET': 660,
        'SRT': -180,
        'SST': 480,
        'SYOT': 180,
        'T': -420,
        'TAHT': -600,
        'TFT': 300,
        'THA': 420,
        'TJT': 300,
        'TKT': 780,
        'TLT': 540,
        'TMT': 300,
        'TOT': 780,
        'TVT': 720,
        'U': -480,
        'UCT': 0,
        'ULAT': 480,
        'USZ1': 120,
        'UTC': 0,
        'UYST': -120,
        'UYT': -180,
        'UZT': 300,
        'V': -540,
        'VET': -210,
        'VLAT': 600,
        'VOLT': 240,
        'VOST': 360,
        'VUT': 660,
        'W': -600,
        'WAKT': 720,
        'WAST': 120,
        'WAT': 60,
        'WEDT': 60,
        'WEST': 60,
        'WET': 0,
        'WIT': 420,
        'WST': 480,
        'X': -660,
        'Y': -720,
        'YAKT': 540,
        'YEKT': 300,
        'Z': 0
    }

    @classmethod
    def add_offset(cls, timestamp: int, tz: str = "UTC") -> int:
        # Get timezone minute offset from tz_offsets
        offset = cls.tz_offsets.get(tz, None)
        if offset is None:
            # Return None if the offset isn't in tz_offsets
            return None

        return (datetime.utcfromtimestamp(timestamp) + relativedelta(minutes=offset)).timestamp()
