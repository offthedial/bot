"""$to profiles get"""
import discord

from offthedialbot import utils

from offthedialbot.commands.profile import create_status_embed


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Get a specific profile."""
    embed = discord.Embed(
        title="Get Profile",
        description="Mention the user you want to get the profile of",
        color=utils.colors.DIALER
    )
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed=embed)
    reply = await ui.get_valid_message(lambda m: len(m.mentions) == 1, {"title": "Invalid Message", "description": "Make sure to send a **mention** of **1** user."})
    member: discord.Member = reply.mentions[0]
    try:
        profile = utils.Profile(member.id)
    except utils.Profile.NotFound:
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Invalid User", description="That user doesn't have a profile.")
    else:
        await ctx.send(embed=create_status_embed(member.display_name, profile))
    await ui.end(None)
