"""$to profiles export"""
from offthedialbot import utils

from ..attendees.export import ToAttendeesExport
from . import user_and_profile


class ToProfilesExport(utils.Command):
    """Export profiles to a csv."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Export profiles to a csv."""
        await ctx.trigger_typing()
        await ToAttendeesExport.export_attendees(ctx, user_and_profile(ctx))
