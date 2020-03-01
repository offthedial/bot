"""$to profiles export"""
from offthedialbot import utils

from . import user_and_profile
from ..attendees.export import export_attendees


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Export profiles to a csv."""
    await ctx.trigger_typing()
    await export_attendees(ctx, user_and_profile(ctx))
