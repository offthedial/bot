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


async def check_valid_attendee(ctx, attendee, competing=True):
    """Check if the attendee is valid or not."""
    try:
        profile = utils.Profile(attendee.id)
    except utils.Profile.NotFound:
        profile = utils.ProfileMeta(attendee.id)
    check = {
        (lambda: not profile): f"`{attendee.display_name}` does not own a profile.",
        (lambda: not profile.get_reg()): f"`{attendee.display_name}` is not competing."
    }
    if not competing:
        check.popitem()

    if any(values := [value for key, value in check.items() if key()]):
        await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Invalid Attendee.", description=values[0])
        return False

    return profile


from . import export, remove
