"""$to attendees"""
from discord.ext import commands

from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Command tools for managing attendees."""
    raise commands.TooManyArguments

def attendee_and_profile(ctx):
    """Create a list of tuples containing an attendee's member object, and profile."""
    profiles: list = [profile["_id"] for profile in utils.dbh.profiles.find({"meta.competing": True}, {"_id": True})]
    return [(ctx.guild.get_member(attendee_id), utils.Profile(attendee_id)) for attendee_id in profiles]
