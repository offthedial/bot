"""$to profiles get"""
import discord

from offthedialbot import utils

from offthedialbot.commands.profile import create_status_embed


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Get a specific profile."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed=discord.Embed())
    for profile, member in await get_profile(ui):
        await ctx.send(embed=create_status_embed(member.display_name, profile))

    await ui.end(None)


async def get_profile(ui):
    ui.embed = discord.Embed(
        title="Get Profiles",
        description="Mention each user you want to get.",
        color=utils.colors.DIALER
    )
    reply = await ui.get_valid_message(lambda m: len(m.mentions), {"title": "Invalid Message", "description": "Make sure to **mention** each user."})
    
    profiles = []
    for member in reply.mentions:
        try:
            profiles.append((utils.Profile(member.id), member))
        except utils.Profile.NotFound:
            await utils.Alert(ui.ctx, utils.Alert.Style.DANGER, title="Invalid User", description=f"{member.display_name} doesn't have a profile.")
    return profiles
