"""Contains tools to help with managing times.""" 
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from offthedialbot import utils


class User:
    """Tools for dealing with users and times."""

    symbols = """
    - years: `Y`, `y`, `yr(s)`, `year(s)`
    - months: `m`, `mon(s)`, `month(s)`
    - weeks: `w`, `W`, `week(s)`
    - days: `d`, `D`, `day(s)`
    - hours: `H`, `h`, `hr(s)`, `hour(s)`
    - minutes: `M`, `min(s)`, `minute(s)`
    - seconds: `S`, `s`, `sec(s)`, `second(s)`
    
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

