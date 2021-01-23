"""$to open"""
import discord

from offthedialbot import utils


class ToNew(utils.Command):
    """ Create a new tournament!

    Steps:
    - Get smash.gg full slug
    - Ask for the type of tournament
    - Add tournament to database
    """

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Open registration for a new tournament!"""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.COMPETING))

        # Steps
        tourney_slug = await cls.get_tourney_slug(ui)
        tourney_type = await cls.get_tourney_type(ui)

        ui.embed.description = "Adding tournament to database..."
        await ui.update()
        await utils.Tournament.new_tournament(slug=tourney_slug, type=tourney_type)
        await ui.end(True)

    @classmethod
    async def get_tourney_slug(cls, ui):
        """Create a new tournament."""
        directions = f"Enter the full tournament slug (`it-s-dangerous-to-go-alone-month-year`)"
        ui.embed.description = directions
        reply = await ui.get_reply()
        return reply.content

    @classmethod
    async def get_tourney_type(cls, ui):
        """Create a new tournament."""
        directions = f"Enter the tournament type (`idtga`, `wl`)"
        ui.embed.description = directions
        reply = await ui.get_valid_message(
            lambda r: r.content.lower() in ["idtga", "wl"],
            {'title': 'Invalid Tournament Type', 'description': directions})
        return reply.content.lower()
