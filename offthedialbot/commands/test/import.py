"""$test import"""
import csv
import aiohttp
from io import StringIO

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
        delete=False,
    )
    await ctx.trigger_typing()

    async with aiohttp.ClientSession() as session:  # Get file from url
        async with session.get(reply.attachments[0].url) as resp:
            file = StringIO((await resp.content.read()).decode("utf-8"))

    reader = csv.reader(file)  # Convert file to csv reader

    ID = 14
    IGN = 1
    SW = 2
    SZ = 3
    TC = 5
    RM = 4
    CB = 6
    SP = 8
    CXP = 9
    SS = 10

    new_profiles = []

    for i, row in enumerate(reader):
        if i < 2:
            continue
        try:
            _id = int(eval(row[ID]))
        except NameError:
            continue

        new_profiles.append({
            "_id": _id,
            "status": {
                "IGN": row[IGN],
                "SW": eval(row[SW]),
                "Ranks": {
                    "Splat Zones": utils.Profile.convert_rank_power(row[SZ]),
                    "Tower Control": utils.Profile.convert_rank_power(row[TC]),
                    "Rainmaker": utils.Profile.convert_rank_power(row[RM]),
                    "Clam Blitz": utils.Profile.convert_rank_power(row[CB]),
                },
            },
            "stylepoints": eval(row[SP]),
            "cxp": int(row[CXP]),
            "signal_strength": int(row[SS]),
            "meta": {
                "competing": False,
                "smashgg": None,
                "banned": None,
                "confirmation_code": None,
            }
        })
    utils.dbh.profiles.insert_many(new_profiles)
    await ui.end(True)
