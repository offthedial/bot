"""$to profiles update cxp"""
import discord

from offthedialbot import utils
from ..get import get_profile
from offthedialbot.commands.profile.update import *


async def main(ctx):
    """Update your competitive experience."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profile, _ = await get_profile(ui)
    ui.embed = create.create_cxp_embed(ctx)

    profile.set_cxp(await create.get_user_cxp(ui))
    profile.write()
    await ui.end(True)
