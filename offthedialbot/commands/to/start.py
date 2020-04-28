"""$to start"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(True)
async def main(ctx):
    """Close registration for the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Closing registration for the tournament...", color=utils.colors.COMPETING))

    # Steps
    await enable_checkin(ui)
    await warn_attendees(ui.ctx)

    await ui.end(True)


async def enable_checkin(ui):
    """Enable the checkin command."""
    ui.embed.description = "Enabling `$checkin`..."
    await ui.update()
    utils.tourney.update(checkin=True)


async def warn_attendees(ctx):
    """Warn attendees who have not checked in yet."""
    for attendee, profile in attendees.attendee_and_profile(ctx):
        utils.time.Timer.schedule(
            utils.time.relativedelta(hours=18) + utils.time.datetime.utcnow(),
            attendee.id, ctx.me.id, style=utils.Alert.Style.WARNING,
            title="You have not checked in yet!",
            description="There are approximately 6 hours left to check-in, so make sure you check-in soon or you will be automatically disqualified.")
