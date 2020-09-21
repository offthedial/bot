"""$to open"""

import discord

from offthedialbot import utils


class ToOpen(utils.Command):
    """ Open registration for a new tournament!

    Steps:
    - Ask for the type of tournament
    - Add tournament to database
    """

    @classmethod
    @utils.deco.require_role("Organiser")
    @utils.deco.tourney(0)
    async def main(cls, ctx):
        """Open registration for a new tournament!"""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.COMPETING))

        # Steps
        tourney_type = await cls.get_tourney_type(ui)
        await cls.new_tourney(ui, tourney_type)

        await ui.end(True)

    @classmethod
    async def get_tourney_type(cls, ui):
        """Create a new tournament."""
        directions = f"Enter the tournament type ({', '.join([tourney.name for tourney in utils.tourney.Type])})"
        ui.embed.description = directions
        reply = await ui.get_valid_message(
            lambda r: getattr(utils.tourney.Type, r.content.upper(), False) is not False,
            {'title': 'Invalid Tournament Type', 'description': directions})
        return getattr(utils.tourney.Type, reply.content.upper())

    @classmethod
    async def new_tourney(cls, ui, tourney_type):
        """Insert tournament into database."""
        ui.embed.description = "Adding tournament to database..."
        await ui.update()
        utils.tourney.new(tourney_type)
