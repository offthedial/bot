"""$to profiles update ss"""
import discord

from offthedialbot import utils
from ..get import get_profile


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Set a user's signal strength."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    profiles = await get_profile(ui)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for profile, member in profiles:
        await ui.run_command(update_ss, profile, member.display_name)

    await ui.end(True)


async def update_ss(ctx, profile, username):
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
        title=f"Set {username}'s Signal Strength",
        description=f"Enter what you want {username}'s signal strength to be, append with a `+` if you want to add signal strength."
    ))
    reply = await ui.get_valid_message(r'^\+?\-?\d{1,}$', {"title": "Invalid Signal Strength", "description": f"Enter what you want {username}'s signal strength to be, append with a `+` if you want to add signal strength."})
    
    if reply.content.startswith("+"):
        ss = profile.get_ss() + int(reply.content[1:])
    else:
        ss = int(reply.content)
    profile.set_ss(ss)
    profile.write()
    await ui.end(True)
