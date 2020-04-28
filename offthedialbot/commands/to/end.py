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
    await remove_all_attendees(ui)
    await delete_tourney(ui)

    await ui.end(True)


async def remove_all_attendees(ui):
    """Loop over each attendee and remove each one from competing."""
    ui.embed.description = "Removing attendees from competing role..."
    await ui.update()
    for attendee, profile in attendees.attendee_and_profile(ui.ctx):
        await attendees.remove.from_competing(ui.ctx, attendee, profile, reason="tournament has ended.")


async def delete_tourney(ui):
    """Delete tournament from database."""
    ui.embed.description = "Deleting tournament from database..."
    await ui.update()
    utils.tourney.delete()
