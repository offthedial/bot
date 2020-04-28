"""$to close"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(False)
async def main(ctx):
    """Start the tournament!"""
    if not utils.tourney.get()['checkin']:
        await utils.Alert(ctx, utils.Alert.Style.DANGER,
            title="Command Failed",
            description="Tournament has already started.")
        raise utils.exc.CommandCancel

    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await close_signup(ui)
    await end_checkin(ui)
    await attendees.remove.disqualified(ctx, checkin=True)
    await attendees.export.export_attendees(ctx, attendees.attendee_and_profile(ctx))
    await ui.end(None)


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


