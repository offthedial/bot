"""$to profiles export"""
from offthedialbot import utils

from . import user_and_profile, attendees


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Export profiles to a csv."""
    await ctx.trigger_typing()
    await attendees.export.export_attendees(ctx, user_and_profile(ctx))
