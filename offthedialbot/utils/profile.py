"""Contains Profile class."""
from datetime import datetime
from typing import Union, Optional

from offthedialbot.utils import dbh


class ProfileMeta:
    """Contains profile metadata uneditable to the user."""

    def __init__(self, _id):
        self.id = _id

        if meta := dbh.metaprofiles.find_one(self.id):
            self.meta = meta
        else:
            self.meta = {
                "_id": self.id,
                "signal": 0,
                "banned": None,
                "smashgg": None,
                "reg": {
                    "reg": False,
                    "code": None,
                }
            }
            dbh.metaprofiles.insert_one(self.meta)

    # Utility Methods
    def write(self):
        """Write profile to database."""
        return dbh.metaprofiles.replace_one({"_id": self.id}, self.meta, upsert=True)

    class NotFound(Exception):
        """Database doesn't return a profile."""

    # Setters
    def inc_ss(self, ss: int):
        """Increases Signal Strength and writes it to the database immediately."""
        dbh.metaprofiles.update_one({"_id": self.id}, {"$inc": {"signal": ss}})
        self.meta["signal"] += ss

    def set_banned(self, banned: Optional[datetime]):
        self.meta["banned"] = banned

    def set_smashgg(self, smashgg):
        self.meta["smashgg"] = smashgg

    def set_reg(self, key="reg", value: Union[bool, Optional[str]] = True):
        self.meta["reg"][key] = value

    # Getters
    def get_ss(self) -> int:
        return self.meta["signal"]

    def get_banned(self) -> Optional[datetime]:
        banned = self.meta["banned"]
        if isinstance(banned, datetime) and datetime.utcnow() < banned:
            return banned
        if banned is True:
            return banned
        return None

    def get_smashgg(self):
        return self.meta["smashgg"]

    def get_reg(self, key="reg") -> Union[bool, str]:
        return self.meta["reg"][key]


class Profile(ProfileMeta):
    """Wraps the DatabaseHandler and provides extra functionality for dealing with profiles."""

    def __init__(self, _id, new=False):
        super().__init__(_id)

        if profile := dbh.profiles.find_one(self.id):
            self.profile = profile
        elif new:
            self.profile: dict = {
                "_id": self.id,
                "IGN": None,
                "SW": None,
                "Ranks": {
                    "Splat Zones": None,
                    "Tower Control": None,
                    "Rainmaker": None,
                    "Clam Blitz": None,
                },
                "stylepoints": [],
                "cxp": 0,
            }
        else:
            raise self.NotFound

    # Profile Methods
    def calculate_elo(self) -> float:
        """Calculate the user's ELO."""
        rank_powers = list(self.profile["Ranks"].values())
        return round(sum(rank_powers) / len(rank_powers), 1)

    def calculate_stylepoints(self, user_playstyles: list) -> list:
        """Calculate a user's stylepoints given playstyles."""
        stylepoints: list = [0, 0, 0]
        for playstyle in user_playstyles:
            stylepoints += [self.playstyles[playstyle]]
            stylepoints: list = [group + add for group, add in zip(stylepoints, self.playstyles[playstyle])]

        return stylepoints

    # Utility Methods
    def write(self):
        """Write profile to database."""
        super().write()
        return dbh.profiles.replace_one({"_id": self.id}, self.profile, upsert=True)

    @staticmethod
    def convert_rank_power(value: Union[str, int, float]) -> Union[str, int, float]:
        """Convert ranks to corresponding powers, and vice versa."""
        ranks = {
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
        }
        ranks.update({v: k for k, v in ranks.items()})

        if isinstance(value, float):
            return "X" + str(value)
        if rank := ranks.get(value, None):
            return rank
        if isinstance(value, str):
            return float(value[1:])
        return None

    playstyles = {
        "frontline": (0, 0, 0),
        "midline": (0, 0, 0),
        "backline": (0, 0, 0),
        "flex": (0, 0, 0),
        "slayer": (0, 0, 0),
        "defensive": (0, 0, 0),
        "objective": (0, 0, 0),
        "support": (0, 0, 0),
    }

    # Setters
    def set_ign(self, ign: str):
        self.profile["IGN"] = ign

    def set_sw(self, sw: int):
        self.profile["SW"] = sw

    def set_rank(self, key, rank: Union[int, float]):
        self.profile["Ranks"][key] = rank

    def set_stylepoints(self, sp: list):
        self.profile["stylepoints"] = sp

    def set_cxp(self, cxp: int):
        self.profile["cxp"] = cxp

    # Getters
    def get_id(self) -> int:
        return self.profile["_id"]

    def get_ign(self) -> str:
        return self.profile["IGN"]

    def get_sw(self) -> int:
        return self.profile["SW"]

    def get_ranks(self) -> dict:
        return self.profile["Ranks"]

    def get_stylepoints(self) -> list:
        return self.profile["stylepoints"]

    def get_cxp(self) -> int:
        return self.profile["cxp"]


def find(profile_id, meta=False) -> Union[Profile, Optional[ProfileMeta]]:
    """Find and return Profile given id."""
    try:
        profile = Profile(profile_id)
    except Profile.NotFound:
        profile = ProfileMeta(profile_id) if meta else None
    return profile
