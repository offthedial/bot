"""$to profiles update ss"""

import discord

from offthedialbot import utils
from . import update_profile_key


class ToProfilesUpdateSs(utils.Command):
    """Set a user's signal strength."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Set a user's signal strength."""
        await update_profile_key(ctx, cls.update_ss)

    @classmethod
    async def update_ss(cls, ctx, profile, username):
        """Modified $profile update command with signal strength."""
        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
            title=f"Enter what you want {username}'s signal strength to be, append with a `+` if you want to add signal strength.",
            description=f"Current Signal Strength: `{profile.get_ss()}`"
        ))
        reply = await ui.get_valid_message(r'^\+?\-?\d{1,}$', {
            "title": "Invalid Signal Strength",
            "description": f"Enter what you want {username}'s signal strength to be, append with a `+` if you want to add signal strength."})

        if reply.content.startswith("+"):
            profile.inc_ss(int(reply.content))
        else:
            profile.inc_ss(int(reply.content) - profile.get_ss())

        await ui.end(True)
