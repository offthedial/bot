"""$to end"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(3)
async def main(ctx):
    """End the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        embed=discord.Embed(title="Ending tournament...", color=utils.colors.COMPETING))

    # Steps
    await remove_all_attendees(ctx)
    utils.tourney.delete()

    await ui.end(True)


async def remove_all_attendees(ctx):
    """Loop over each attendee and remove each one from competing."""
    for attendee, profile in attendees.attendee_and_profile(ctx):
        await attendees.remove.from_competing(ctx, attendee, profile, reason="tournament has ended.")
