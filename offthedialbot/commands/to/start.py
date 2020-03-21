"""$to start"""
import discord

from offthedialbot import utils
from . import attendees


@utils.deco.require_role("Organiser")
@utils.deco.tourney(False)
async def main(ctx):
    """Start the tournament!"""
    await check_tourney_checkin(ctx)

    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

    await end_checkin(ui)
    await attendees.remove.disqualified(ctx, checkin=True)
    await attendees.export.export_attendees(ctx, attendees.attendee_and_profile(ctx))
    await ui.end(None)


async def end_checkin(ui):
    """Disable the checkin command."""
    ui.embed.description = "Disabling `$checkin`..."
    await ui.update()
    checkin_cmd = ui.ctx.bot.get_command("checkin")
    checkin_cmd.enabled = False


async def check_tourney_checkin(ctx):
    """Make sure the tournament checkin is enabled so it is able to be started."""
    if not ctx.bot.get_command("checkin").enabled:
        await utils.Alert(ctx, utils.Alert.Style.DANGER,
                          title="Command Failed",
                          description="Tournament has already started.")
        raise utils.exc.CommandCancel
