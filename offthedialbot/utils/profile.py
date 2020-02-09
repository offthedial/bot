"""Contains Profile class."""
from typing import Union


class Profile:
    """Provides helpful functions for working with profiles."""
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

    def __init__(self, profile: dict = None):
        self.profile = profile if profile else {
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
            "stylepoints": [],  # Groups A, B, and C.
            "cxp": 0,
            "signal_strength": 0,
            "meta": {
                "competing": False,
                "smashgg": None,
                "banned": None,
            }
        }

    # Setters
    def set_status_key(self, key: str, value):
        """Set status key to value."""
        self.profile["status"][key] = value
        return self.profile["status"][key]

    def set_rank(self, key: str, rank: Union[str, int, float]) -> Union[int, float]:
        """Set rank at specified key."""
        self.profile["status"]["Ranks"][key] = (self.convert_rank_power(rank) if isinstance(rank, str) else rank)
        return self.profile["status"]["Ranks"][key]

    def set_stylepoints(self, stylepoints: list) -> list:
        """Sets stylepoints."""
        self.profile["stylepoints"] = stylepoints
        return self.profile["stylepoints"]

    def set_cxp(self, cxp: int) -> int:
        """Sets competitive experience."""
        self.profile["cxp"] = cxp
        return self.profile["cxp"]

    def add_signal_strength(self, ss: int) -> int:
        """Add to signal strength."""
        self.profile["signal_strength"] += ss
        return self.profile["signal_strength"]

    def set_competing(self, competing: bool) -> bool:
        """Set competing."""
        self.profile["meta"]["competing"] = competing
        return self.profile["meta"]["competing"]

    # Getters
    def get_id(self) -> int:
        """Returns discord id of profile."""
        return self.profile["_id"]

    def get_status(self, key: str = None) -> dict:
        """Returns profile status."""
        return self.profile["status"][key] if key else self.profile["status"]

    def get_ranks(self, key: str = None) -> dict:
        """Returns profile ranks."""
        return self.profile["status"]["Ranks"][key] if key else self.profile["status"]["Ranks"]

    def get_stylepoints(self) -> list:
        """Returns stylepoints."""
        return self.profile["stylepoints"]

    def get_cxp(self) -> int:
        """Returns competitive experience."""
        return self.profile["cxp"]

    def get_signal_strength(self) -> int:
        """Returns signal strength."""
        return self.profile["signal_strength"]

    def is_competing(self) -> bool:
        """Returns whether profile is competing."""
        return self.profile["meta"]["competing"]

    def smashgg_id(self):
        """Returns smash.gg id."""
        return self.profile["meta"]["smashgg"]

    def is_banned(self):
        """Returns whether the user is banned or not."""
        return self.profile["meta"]["banned"]

    def calculate_elo(self) -> float:
        """Calculate the user's ELO."""
        rank_powers = [rank for rank in self.profile["status"]["Ranks"].values()]
        return round(sum(rank_powers) / len(rank_powers), 1)

    def calculate_stylepoints(self, user_playstyles: list) -> list:
        """Calculate a user's stylepoints given their playstyles."""
        stylepoints: list = [0, 0, 0]
        for playstyle in user_playstyles:
            stylepoints += [self.playstyles[playstyle]]
            stylepoints: list = [group + add for group, add in zip(stylepoints, self.playstyles[playstyle])]

        return stylepoints

    def dict(self) -> dict:
        """Returns the dictionary representation of a profile."""
        return self.profile

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
