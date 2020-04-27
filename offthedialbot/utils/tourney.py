"""Contains tournament."""
from enum import IntEnum

from offthedialbot import utils


class Type(IntEnum):
    """Enum to store tournament types."""
    IDTGA = 0
    WL = 1
    STORY = 2


links = [
    'https://smash.gg/idtga',
    'https://smash.gg/wl',
    'https://smash.gg/storymode',
]


rules = [
    'https://docs.google.com/document/d/1f8j-DwNGEkgwpoyroJQ1jAg0v-sGWgWJfeSYf8jFV78',
    'https://docs.google.com/document/d/1yOE-BHw4rxX9SJCUNO8NnCn70KBrQ4gomEPcqWOckGU',
    'https://docs.google.com/document/d/1f8j-DwNGEkgwpoyroJQ1jAg0v-sGWgWJfeSYf8jFV78',
]


def new(tourney_type: Type):
    """Start a new tournament."""
    return utils.dbh.to.insert_one({
        "_id": 0,
        "type": tourney_type,
        "reg": True,
        "checkin": False,
    })


def get():
    """Get the tournament database entry."""
    return utils.dbh.to.find_one({"_id": 0})


def delete():
    """Delete the tournament from the database."""
    return utils.dbh.to.find_one_and_delete({"_id": 0})


def update(reg: bool = None, checkin: bool = None):
    """Set tournament registration and check-in."""
    tourney = get()
    if reg is None:
        reg = tourney['reg']
    if checkin is None:
        checkin = tourney['checkin']
    return utils.dbh.to.update_one({"_id": 0}, {"$set": {"reg": reg, "checkin": checkin}})
