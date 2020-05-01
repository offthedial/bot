"""$to profiles update"""
import discord

from offthedialbot import utils
from offthedialbot.commands.profile.update import ProfileUpdate
from ..get import ToProfilesGet


class ToProfilesUpdate(utils.Command):
    """Update user's profile."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Update user's profile."""
        await update_profile_key(ctx, cls.profile_update)

    @classmethod
    async def profile_update(cls, ctx, profile, username):
        """Modified $profile update command."""
        title = f"{username}'s Status"
        await ProfileUpdate.update_profile(ctx, profile, title)


async def update_profile_key(ctx, command):
    """Update other profile keys."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Updating profiles...", color=utils.colors.DIALER))
    profiles = await ToProfilesGet.get_profiles(ui)
    for profile, member in profiles:
        await ui.run_command(command, profile, member.display_name)

    await ui.end(True)
