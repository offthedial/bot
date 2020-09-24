"""$test restore"""

from enum import IntEnum
import csv
from io import StringIO

import aiohttp
import discord

from offthedialbot import utils
from offthedialbot.commands.profile.create import ProfileCreate


class ToProfilesRestore(utils.Command):
    """Restore profiles from backup."""

    @classmethod
    async def main(cls, ctx):
        """Restore profiles from backup."""
        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
            title="Please upload a valid profiles export."
        ))
        reply: discord.Message = await ui.get_valid('message',
            lambda m: getattr(m, "attachments", []),
            {"title": "Invalid profiles export", "description": "Please upload a `profiles.csv`."},
            delete=False)

        async with ctx.typing():

            reader = csv.reader(await cls.create_file(reply))
            await reply.delete()

            profiles, metaprofiles = cls.new_profiles(reader)
            utils.dbh.profiles.insert_many(profiles)
            utils.dbh.metaprofiles.insert_many(metaprofiles)

        await ui.end(True)

    @classmethod
    async def create_file(cls, reply):
        """Create csv file from reply."""
        async with aiohttp.ClientSession() as session:  # Get file from url
            async with session.get(reply.attachments[0].url) as resp:
                file = StringIO((await resp.content.read()).decode("utf-8"))
        return file

    @classmethod
    def new_profiles(cls, reader):
        """Return a list of profiles from csv reader."""
        profiles = []
        metaprofiles = []

        for i, row in enumerate(reader):
            if (_id := cls.skip(i, row)) is True:
                continue

            profiles.append({
                "_id": _id,
                "IGN": row[cls.Column.IGN],
                "SW": ProfileCreate.parse_reply('SW', row[cls.Column.SW]),
                "Ranks": {
                    "Splat Zones": ProfileCreate.parse_reply('Ranks', row[cls.Column.SZ]),
                    "Tower Control": ProfileCreate.parse_reply('Ranks', row[cls.Column.TC]),
                    "Rainmaker": ProfileCreate.parse_reply('Ranks', row[cls.Column.RM]),
                    "Clam Blitz": ProfileCreate.parse_reply('Ranks', row[cls.Column.CB]),
                },
                "stylepoints": eval(row[cls.Column.SP]),
                "cxp": int(row[cls.Column.CXP]),
            })
            metaprofiles.append({
                "_id": _id,
                "signal": int(row[cls.Column.SS]),
                "smashgg": None,
                "banned": None,
                "reg": {
                    "reg": False,
                    "code": None,
                }
            })
        return profiles, metaprofiles

    @classmethod
    def skip(cls, i, row):
        """Check if a row should be skipped."""
        if i < 2:
            return True
        try:
            _id = int(row[cls.Column.ID][2:-1])
        except NameError:
            return True
        else:
            return _id

    @classmethod
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
