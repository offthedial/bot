"""$to profiles update stylepoints"""
import discord

from offthedialbot import utils
from ..get import get_profile
from offthedialbot.commands.profile.update import *


async def main(ctx):
    """Update your stylepoints."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profile, _ = await get_profile(ui)
    ui.embed = create.create_stylepoints_embed(ctx)

    profile.set_stylepoints(await create.get_user_stylepoints(ui))
    profile.write()
    await ui.end(True)
