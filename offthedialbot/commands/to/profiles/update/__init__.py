"""$to profiles update"""
import discord

from offthedialbot.commands.profile.update import *
from ..get import get_profiles


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Update user's profile."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profiles = await get_profiles(ui)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for profile, member in profiles:
        await ui.run_command(profile_update, profile, member.display_name)

    await ui.end(True)


async def profile_update(ctx, profile, username):
    """Modified $profile update command."""
    title = f"{username}'s Status"
    await update_profile(ctx, profile, title)
