"""$to profiles"""

from discord.ext import commands

from offthedialbot import utils


class ToProfiles(utils.Command):
    """Command tools for managing profiles."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Command tools for managing profiles."""
        raise commands.TooManyArguments


def user_and_profile(ctx):
    """Create a list of tuples containing an user's member object, and profile."""
    profiles: list = [profile["_id"] for profile in utils.dbh.profiles.find({}, {"_id": True})]
    return [(ctx.guild.get_member(user_id), utils.Profile(user_id)) for user_id in profiles]
