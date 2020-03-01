"""$to profiles update stylepoints"""
import discord

from offthedialbot import utils
from ..get import get_profile
from offthedialbot.commands.profile.update import *


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Update user's stylepoints."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profiles = await get_profile(ui)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for profile, member in profiles:
        await ui.run_command(update_stylepoints, profile, member.display_name)

    await ui.end(True)


async def update_stylepoints(ctx, profile, username):
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_stylepoints_embed(ctx))
    ui.embed.title = f"{username}'s Stylepoints"

    profile.set_stylepoints(await create.get_user_stylepoints(ui))
    profile.write()
    await ui.end(True)
