"""$to start"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(False)
async def main(ctx):
    """Start the tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await end_checkin(ui)
    await remove_inactives(ctx)
    await attendees.export.export_attendees(ctx)
    await ui.end(None)


async def end_checkin(ui):
    """Disable the checkin command."""
    ui.embed.description = "Disabling `$checkin`..."
    await ui.update()
    checkin_cmd = ui.ctx.bot.get_command("checkin")
    checkin_cmd.enabled = False


async def remove_inactives(ctx):
    """Remove attendees who have not checked in."""
    for attendee, profile in attendees.attendee_and_profile(ctx):

        if (attendee is None) or (not "Checked In" in [role.name for role in attendee.roles]):
            await attendees.remove.remove_attendee(ctx, attendee, profile)
