"""$to close"""
import discord

from offthedialbot import utils
from . import attendees


class ToClose(utils.Command):
    """ Close registration and end checkin for the tournament.

    Steps:
    - Close registration
    - End checkin
    - Remove disqualified attendees
    - Export attendees
    """

    @classmethod
    @utils.deco.require_role("Organiser")
    @utils.deco.tourney(2)
    async def main(cls, ctx):
        """Close registration and end checkin for the tournament."""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Commencing tournament...", color=utils.colors.COMPETING))

        await cls.close_reg(ui)
        await cls.end_checkin(ui)
        await cls.remove_disqualified(ui)
        await cls.export_attendees(ui)

        await ui.end(True,
            title=":incoming_envelope: *Exporting attendees complete!*",
            description="Download the spreadsheet below. \U0001f4e5")

    @classmethod
    async def close_reg(cls, ui):
        """Set tournament reg to false."""
        ui.embed.description = "Closing registration..."
        await ui.update()
        utils.tourney.update(reg=False)

    @classmethod
    async def end_checkin(cls, ui):
        """Disable the checkin command."""
        ui.embed.description = "Disabling `$checkin`..."
        await ui.update()
        utils.tourney.update(checkin=False)

    @classmethod
    async def remove_disqualified(cls, ui):
        """Remove disqualified members."""
        ui.embed.description = "Removing disqualified attendees..."
        await ui.update()
        await attendees.remove.disqualified(ui.ctx, left=True, checkin=True)

    @classmethod
    async def export_attendees(cls, ui):
        """Automatically export attendees."""
        ui.embed.description = "Exporting attendees..."
        await ui.update()
        file = attendees.export.create_file(ui.ctx, attendees.attendee_and_profile(ui.ctx))
        await ui.ctx.send(file=file)
