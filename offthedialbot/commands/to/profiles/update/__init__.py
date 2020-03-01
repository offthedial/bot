"""$to profiles update"""
import discord

from offthedialbot import utils
from ..get import get_profile
from offthedialbot.commands.profile.update import *


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Update user's profile."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profiles = await get_profile(ui)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for profile, member in profiles:
        await ui.run_command(update_profile, profile, member.display_name)

    await ui.end(True)


async def update_profile(ctx, profile, username):
    embed, emojis = create_update_embed(ctx, profile)
    embed.title = f"{username}'s Status"

    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    reply = await ui.get_reply("reaction_add", valid_reactions=emojis)
    index: int = emojis.index(reply.emoji)
    field = create.clean_status_key(profile, list(profile.get_status().keys())[index])
    await wait_profile_field(ui, profile, index, field)
