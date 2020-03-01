"""$to profiles update"""
import discord

from offthedialbot import utils
from ..get import get_profile
from offthedialbot.commands.profile.update import *


async def main(ctx):
    """Update your profile."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profile, _ = await get_profile(ui)
    ui.embed, emojis = create_update_embed(ctx, profile)

    reply = await ui.get_reply("reaction_add", valid_reactions=emojis)
    index: int = emojis.index(reply.emoji)
    field = create.clean_status_key(profile, list(profile.get_status().keys())[index])
    await wait_profile_field(ui, profile, index, field)
