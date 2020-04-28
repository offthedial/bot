"""$to close"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(2)
async def main(ctx):
    """Close registration and end checkin for the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await close_signup(ui)
    await end_checkin(ui)
    await remove_disqualified(ui)
    await export_attendees(ui)

    await ui.end(True,
        title=":incoming_envelope: *Exporting attendees complete!*",
        description="Download the spreadsheet below. \U0001f4e5")


async def close_signup(ui):
    """Set tournament reg to false."""
    ui.embed.description = "Closing registration..."
    await ui.update()
    utils.tourney.update(reg=False)


async def end_checkin(ui):
    """Disable the checkin command."""
    ui.embed.description = "Disabling `$checkin`..."
    await ui.update()
    utils.tourney.update(checkin=False)


async def remove_disqualified(ui):
    """Remove disqualified members."""
    ui.embed.description = "Removing disqualified members..."
    await ui.update()
    await attendees.remove.disqualified(ui.ctx, left=True, checkin=True)


async def export_attendees(ui):
    """Automatically export attendees."""
    ui.embed.description = "Exporting attendees..."
    await ui.update()
    file = attendees.export.create_file(ui.ctx, attendees.attendee_and_profile(ui.ctx))
    await ui.ctx.send(file=file)
