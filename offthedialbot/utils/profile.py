"""Contains Profile class."""
from datetime import datetime
from typing import Union

from offthedialbot.utils import dbh


class Profile:
    """Wraps the DatabaseHandler and provides extra functionality for dealing with profiles."""

    def __init__(self, _id, new=False):
        self.id = _id
        self.new = new

        if profile := dbh.profiles.find_one(self.id):
            self.profile = profile
        elif new:
            self.profile: dict = {
                "_id": _id,
                "status": {
                    "IGN": None,
                    "SW": None,
                    "Ranks": {
                        "Splat Zones": None,
                        "Rainmaker": None,
                        "Tower Control": None,
                        "Clam Blitz": None,
                    },
                },
                "stylepoints": [],
                "cxp": 0,
                "signal_strength": 0,
                "meta": {
                    "competing": False,
                    "smashgg": None,
                    "banned": None,
                    "confirmation_code": None,
                }
            }
        else:
            raise self.NotFound

    # Profile Methods
    def calculate_elo(self) -> float:
        """Calculate the user's ELO."""
        rank_powers = [rank for rank in self.profile["status"]["Ranks"].values()]
        return round(sum(rank_powers) / len(rank_powers), 1)

    def calculate_stylepoints(self, user_playstyles: list) -> list:
        """Calculate a user's stylepoints given playstyles."""
        stylepoints: list = [0, 0, 0]
        for playstyle in user_playstyles:
            stylepoints += [self.playstyles[playstyle]]
            stylepoints: list = [group + add for group, add in zip(stylepoints, self.playstyles[playstyle])]

        return stylepoints

    # Utility Methods
    def read(self):
        """Update profile from database."""
        assert not new
        self.profile = dbh.profiles.find_one(self.id)

    def write(self):
        """Write profile to database."""
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
        elif rank := ranks.get(value, None):
            return rank
        elif isinstance(value, str):
            return float(value[1:])

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

    class NotFound(Exception):
        """Database doesn't return a profile."""
        pass

    # Setters
    def set_status(self, key, value):
        self.profile["status"][key] = value

    def set_ign(self, ign: str):
        self.profile["status"]["IGN"] = ign

    def set_sw(self, sw: int):
        self.profile["status"]["SW"] = sw

    def set_rank(self, key, rank: Union[int, float]):
        self.profile["status"]["Ranks"][key] = rank

    def set_sz(self, sz: Union[int, float]):
        self.profile["status"]["Ranks"]["Splat Zones"] = sz

    def set_rm(self, rm: Union[int, float]):
        self.profile["status"]["Ranks"]["Rainmaker"] = rm

    def set_tc(self, tc: Union[int, float]):
        self.profile["status"]["Ranks"]["Tower Control"] = tc

    def set_cb(self, cb: Union[int, float]):
        self.profile["status"]["Ranks"]["Clam Blitz"] = cb

    def set_stylepoints(self, sp: list):
        self.profile["stylepoints"] = sp

    def set_cxp(self, cxp: int):
        self.profile["cxp"] = cxp

    def set_ss(self, ss: int):
        self.profile["signal_strength"] = ss

    def set_competing(self, competing: bool):
        self.profile["meta"]["competing"] = competing

    def set_smashgg(self, smashgg):
        self.profile["meta"]["smashgg"] = smashgg

    def set_banned(self, banned: Union[None, datetime]):
        self.profile["meta"]["banned"] = banned

    def set_cc(self, cc: str):
        self.profile["meta"]["confirmation_code"] = cc

    # Getters
    def get_status(self) -> dict:
        return self.profile["status"]

    def get_ign(self) -> str:
        return self.profile["status"]["IGN"]

    def get_sw(self) -> int:
        return self.profile["status"]["SW"]

    def get_ranks(self) -> dict:
        return self.profile["status"]["Ranks"]

    def get_sz(self) -> Union[int, float]:
        return self.profile["status"]["Ranks"]["Splat Zones"]

    def get_rm(self) -> Union[int, float]:
        return self.profile["status"]["Ranks"]["Rainmaker"]

    def get_tc(self) -> Union[int, float]:
        return self.profile["status"]["Ranks"]["Tower Control"]

    def get_cb(self) -> Union[int, float]:
        return self.profile["status"]["Ranks"]["Clam Blitz"]

    def get_stylepoints(self) -> list:
        return self.profile["stylepoints"]

    def get_cxp(self) -> int:
        return self.profile["cxp"]

    def get_ss(self) -> int:
        return self.profile["signal_strength"]

    def get_competing(self) -> bool:
        return self.profile["meta"]["competing"]

    def get_smashgg(self):
        return self.profile["meta"]["smashgg"]

    def get_banned(self) -> Union[None, datetime]:
        banned = self.profile["meta"]["banned"]
        if isinstance(banned, datetime) and datetime.utcnow() < banned:
            return banned
        elif banned is True:
            return banned

    def get_cc(self) -> str:
        return self.profile["meta"]["confirmation_code"]
