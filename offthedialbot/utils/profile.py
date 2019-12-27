from typing import Union


class Profile:
    """User profile class."""
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
            "meta": {
                "currently_competing": False,
                "previous_tourneys": [],
                "dropout_ban": None,
            }
        }

    # Setters
    def set_status(self, key: str, value):
        """Set status key to value."""
        self.profile["status"][key] = value
        return self.profile["status"][key]

    def set_rank(self, key: str, rank: Union[str, int, float]):
        """Set rank at specified key."""
        self.profile["status"]["Ranks"][key] = (self.convert_rank_power(rank) if isinstance(rank, str) else rank)
        return self.profile["status"]["Ranks"][key]

    def set_stylepoints(self, stylepoints: list) -> list:
        """Sets stylepoints."""
        self.profile["stylepoints"] = stylepoints
        return self.profile["stylepoints"]

    def set_cxp(self, cxp: int) -> int:
        """Sets competitive experience"""
        self.profile["cxp"] = cxp
        return self.profile["cxp"]

    # Getters
    def get_status(self) -> dict:
        """Returns profile status."""
        return self.profile["status"]

    def get_ranks(self) -> dict:
        """Returns profile ranks."""
        return self.profile["status"]["Ranks"]

    def get_stylepoints(self) -> list:
        """Returns stylepoints"""
        return self.profile["stylepoints"]

    def get_cxp(self) -> int:
        """Returns competitive experience."""
        return self.profile["cxp"]

    def calculate_elo(self) -> int:
        """Calculate the user's points."""
        pass

    def calculate_stylepoints(self, user_playstyles: list):
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
