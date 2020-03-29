"""$to profiles update ss"""
import discord

from offthedialbot import utils
from .get import get_role_profiles


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Distribute Signal Strength by role!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed())
    role_profiles = await get_role_profiles(ui, meta=True)
    ui.embed = discord.Embed(title="Updating profiles...", color=utils.colors.DIALER)
    for role, profiles in role_profiles.items():
        await ui.run_command(distribute_ss, role, profiles)

    await ui.end(True)


async def distribute_ss(ctx, role, profiles):
    """Distribute signal strength to everyone in the role."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
        title=f"Distribute Signal Strength for {role.name}.",
        description=f"Enter how much signal strength to give to everyone in {role.mention}."
    ))
    reply = await ui.get_valid_message(r'^\+?\-?\d{1,}$', {
        "title": "Invalid Signal Strength",
        "description": f"Enter how much signal strength to give to everyone in {role.mention}."})
    print("ROLE: "+role.name)
    for profile, member in profiles:
        profile.inc_ss(int(reply.content))
        print(member)

    await ui.end(True)
