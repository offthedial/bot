"""$to profiles update ss"""
import discord

from offthedialbot import utils
from ..get import get_profile

async def main(ctx):
    """Set a user's signal strength."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profile, _ = await get_profile(ui)

    await set_ss(ui, profile)
    profile.write()
    await ui.end(True)


async def set_ss(ui: utils.CommandUI, profile):
    ui.embed = discord.Embed(
        title="Set User Signal Strength",
        description="Enter what you want the user's signal strength to be, append with a `+` if you want to add signal strength."
    )
    reply = await ui.get_valid_message(r'^\+?\-?\d{1,}$', {"title": "Invalid Signal Strength", "description": "Enter what you want the user's signal strength to be, append with a `+` if you want to add signal strength."})
    
    if reply.content.startswith("+"):
        ss = profile.get_ss() + int(reply.content[1:])
    else:
        ss = int(reply.content)
    profile.set_ss(ss)
