"""$to close"""
import discord

from offthedialbot import utils
from .attendees import attendee_and_profile


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
    await warn_attendees(ui.ctx)


async def warn_attendees(ctx):
    """Warn attendees who have not checked in yet."""
    for attendee, profile in attendee_and_profile(ctx):
        utils.time.Timer.schedule(utils.time.relativedelta(hours=18) + utils.time.datetime.utcnow(),
            attendee.id, ctx.me.id,
            style=utils.Alert.Style.WARNING,
            title="You have not checked in yet!",
            description="There are approximately 6 hours left to check-in, so make sure you check-in soon or you will be automatically disqualified."
        )