"""$to end"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(False)
async def main(ctx):
    """End the tournament."""
    await check_tourney_started(ctx)

    ui: utils.CommandUI = await utils.CommandUI(ctx, embed=discord.Embed(title="Ending tournament...", color=utils.colors.COMPETING))

    # Steps
    await remove_all_attendees(ctx)
    utils.dbh.end_tourney()

    await ui.end(True)


async def remove_all_attendees(ctx):
    for attendee, profile in attendees.attendee_and_profile(ctx):
        await attendees.remove.remove_attendee(ctx, attendee, profile, reason="tournament has ended.")


async def check_tourney_started(ctx):
    if ctx.bot.get_command("checkin").enabled:
        await utils.Alert(ctx, utils.Alert.Style.DANGER,
            title="Command Failed",
            description="Tournament has not started yet."
        )
        raise utils.exc.CommandCancel
