"""$to close"""
import discord

from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney(True)
async def main(ctx):
    """Close registration for the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Closing registration for the tournament...", color=utils.colors.COMPETING))

    # Steps
    await close_signup(ui)
    await start_checkin(ui)

    await ui.end(True)


async def close_signup(ui):
    """Set tournament reg to false."""
    ui.embed.description = "Closing registration..."
    await ui.update()
    utils.dbh.set_tourney_reg(False)


async def start_checkin(ui):
    """Enable the checkin command."""
    ui.embed.description = "Enabling `$checkin`..."
    await ui.update()
    checkin_cmd = ui.ctx.bot.get_command("checkin")
    checkin_cmd.enabled = True
