"""$to open"""
import discord

from offthedialbot import utils


class ToNew(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """ Open registration for a new tournament!

        Steps:
        - Get smash.gg full slug.
        - Get tournament type.
        - Add tournament data to database.
        """
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.COMPETING))

        # Steps
        tourney_slug = await cls.get_tourney_slug(ui)
        tourney_type = await cls.get_tourney_type(ui)

        ui.embed.description = "Adding tournament to database..."
        await ui.update()
        tourney = await utils.Tournament.new_tourney(slug=tourney_slug, type=tourney_type)
        await ui.end(utils.Alert.create_embed(utils.Alert.Style.SUCCESS,
            title="Tournament Created",
            description="\n".join([
                f"Name: `{tourney.dict['smashgg']['name']}`",
                f"Start.gg Slug: `{tourney_slug}`",
                f"Tournament Type: `{tourney_type}`"
            ])))

    @classmethod
    async def get_tourney_slug(cls, ui):
        """Create a new tournament."""
        directions = f"Enter the full tournament slug (`it-s-dangerous-to-go-alone-month-20XX`)"
        ui.embed.description = directions
        reply = await ui.get_reply()
        return reply.content

    @classmethod
    async def get_tourney_type(cls, ui):
        """Create a new tournament."""
        directions = f"Enter the tournament type (`idtga`, `wl`)"
        ui.embed.description = directions
        reply = await ui.get_reply()
        return reply.content.lower()
