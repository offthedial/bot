"""$to start"""
import discord

from offthedialbot import utils
from .attendees import export


@utils.deco.require_role("Organiser")
@utils.deco.tourney(False)
async def main(ctx):
    """Start the tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await end_checkin(ui)
    await export.export_profiles(ui, {"meta.competing": True})


async def end_checkin(ui):
    """Disable the checkin command."""
    ui.embed.description = "Disabling `$checkin`..."
    await ui.update()
    checkin_cmd = ui.ctx.bot.get_command("checkin")
    checkin_cmd.enabled = False
