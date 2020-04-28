"""$to start"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(1)
async def main(ctx):
    """Start checkin for the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Closing registration for the tournament...", color=utils.colors.COMPETING))

    # Steps
    await enable_checkin(ui)
    await warn_attendees(ui)

    await ui.end(True)


async def enable_checkin(ui):
    """Enable the checkin command."""
    ui.embed.description = "Enabling `$checkin`..."
    await ui.update()
    utils.tourney.update(checkin=True)


async def warn_attendees(ui):
    """Warn attendees who have not checked in yet."""
    ui.embed.description = "Scheduling check-in warnings in `18` hours..."
    await ui.update()
    for attendee, profile in attendees.attendee_and_profile(ui.ctx):
        utils.time.Timer.schedule(
            utils.time.relativedelta(hours=18) + utils.time.datetime.utcnow(),
            attendee.id, ui.ctx.me.id, style=utils.Alert.Style.WARNING,
            title="You have not checked in yet!",
            description="There are approximately 6 hours left to check-in, so make sure you check-in soon or you will be automatically disqualified.")
