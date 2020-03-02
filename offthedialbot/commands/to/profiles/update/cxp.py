"""$to profiles update cxp"""
import discord

from offthedialbot import utils
from ..get import get_profiles
from offthedialbot.commands.profile.update import *


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Update user's competitive experience."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profiles = await get_profiles(ui)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for profile, member in profiles:
        await ui.run_command(update_cxp, profile, member.display_name)

    await ui.end(True)


async def update_cxp(ctx, profile, username):
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_cxp_embed(ctx))
    ui.embed.title = f"{username}'s Competitive Experience"

    profile.set_cxp(await create.get_user_cxp(ui))
    profile.write()
    await ui.end(True)
