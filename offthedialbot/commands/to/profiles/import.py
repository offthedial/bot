"""$test import"""
from enum import IntEnum
import csv
from io import StringIO

import aiohttp
import discord

from offthedialbot import utils


async def main(ctx):
    """Temporary command to import from backup."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
        title="Please upload a valid profiles export."
    ))
    reply: discord.Message = await ui.get_valid('message',
        lambda m: getattr(m, "attachments", []),
        {"title": "Invalid profiles export", "description": "Please upload a `profiles.csv`."},
        delete=False)

    async with ctx.typing():

        reader = csv.reader(await create_file(reply))
        await reply.delete()
        utils.dbh.profiles.insert_many(new_profiles(reader))

    await ui.end(True)


async def create_file(reply):
    """Create csv file from reply."""
    async with aiohttp.ClientSession() as session:  # Get file from url
        async with session.get(reply.attachments[0].url) as resp:
            file = StringIO((await resp.content.read()).decode("utf-8"))
    return file


def new_profiles(reader):
    """Return a list of profiles from csv reader."""
    profiles = []

    for i, row in enumerate(reader):
        if (_id := skip(i, row)) is True:
            continue

        profiles.append({
            "_id": _id,
            "status": {
                "IGN": row[Column.IGN],
                "SW": eval(row[Column.SW]),
                "Ranks": {
                    "Splat Zones": utils.Profile.convert_rank_power(row[Column.SZ]),
                    "Tower Control": utils.Profile.convert_rank_power(row[Column.TC]),
                    "Rainmaker": utils.Profile.convert_rank_power(row[Column.RM]),
                    "Clam Blitz": utils.Profile.convert_rank_power(row[Column.CB]),
                },
            },
            "stylepoints": eval(row[Column.SP]),
            "cxp": int(row[Column.CXP]),
            "signal_strength": int(row[Column.SS]),
            "meta": {
                "competing": False,
                "smashgg": None,
                "banned": None,
                "confirmation_code": None,
            }
        })
    return profiles


def skip(i, row):
    """Check if a row should be skipped."""
    if i < 2:
        return True
    try:
        _id = int(eval(row[Column.ID]))
    except NameError:
        return True
    else:
        return _id


class Column(IntEnum):
    """Column names for the csv."""
    ID = 14
    IGN = 1
    SW = 2
    SZ = 3
    TC = 4
    RM = 5
    CB = 6
    SP = 8
    CXP = 9
    SS = 10
