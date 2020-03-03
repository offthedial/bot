"""Contains tools to help with managing times.""" 
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

## Things to keep in mind
# Parse user-inputted times (3h, 4d, 5M) to datetime
# Support waiting for extended periods of time
# Persist past bot restart


class User:
    """Tools for dealing with users and times."""

    symbols = """
    - years: `Y`, `y`, `yrs`, `year`, `years`
    - months: `m`, `mon`, `month`, `months`
    - weeks: `w`, `W`, `week`, `weeks`
    - days: `d`, `D`, `day`, `days`
    - hours: `H`, `h`, `hrs`, `hour`, `hours`
    - minutes: `M`, `min`, `minute`, `minutes`
    - seconds: `S`, `s`, `sec`, `second`, `seconds`
    
    Units must be provided in descending order of magnitude.
    """
    
    complied = re.compile(
        r"((?P<years>\d+?) ?(years|year|yrs|Y|y) ?)?"
        r"((?P<months>\d+?) ?(months|month|mon|m) ?)?"
        r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
        r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
        r"((?P<hours>\d+?) ?(hours|hour|hrs|H|h) ?)?"
        r"((?P<minutes>\d+?) ?(minutes|minute|min|M) ?)?"
        r"((?P<seconds>\d+?) ?(seconds|second|sec|S|s))?"
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

