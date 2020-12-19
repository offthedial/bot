"""$to start"""

import discord

from offthedialbot import utils
from . import attendees


class ToStart(utils.Command):
    """ Start checkin for the tournament.

    Steps:
    - Enable check-in
    - Schedule check-in warnings
    """

    @classmethod
    @utils.deco.require_role("Staff")
    @utils.deco.tourney(1)
    async def main(cls, ctx):
        """Start checkin for the tournament."""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Closing registration for the tournament...", color=utils.colors.COMPETING))

        # Steps
        await cls.enable_checkin(ui)
        await cls.warn_attendees(ui)

        await ui.end(True)

    @classmethod
    async def enable_checkin(cls, ui):
        """Enable the checkin command."""
        ui.embed.description = "Enabling `$checkin`..."
        await ui.update()
        utils.tourney.update(checkin=True)

    @classmethod
    async def warn_attendees(cls, ui):
        """Warn attendees who have not checked in yet."""
        ui.embed.description = "Scheduling check-in warnings in `18` hours..."
        await ui.update()
        for attendee, profile in attendees.attendee_and_profile(ui.ctx):
            utils.time.Timer.schedule(
                utils.time.relativedelta(hours=18) + utils.time.datetime.utcnow(),
                attendee.id, ui.ctx.me.id, style=utils.Alert.Style.WARNING,
                title="You have not checked in yet!",
                description="There are approximately 6 hours left to check-in, so make sure you check-in soon or you will be automatically disqualified.")
