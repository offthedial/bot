"""$to open"""
import discord

from offthedialbot import utils


class ToNew(utils.Command):

    TYPE = "idtga"

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """ Open registration for a new tournament!

        Steps:
        - Get sendou.ink tournament id.
        - Add tournament data to database.
        """
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.COMPETING))

        # Steps
        sendou_id = await cls.get_sendou_id(ui)

        ui.embed.description = "Adding tournament to database..."
        await ui.update()
        tourney = await utils.Tournament.new_tourney(sendou_id=sendou_id, type=cls.TYPE)
        await ui.end(utils.Alert.create_embed(utils.Alert.Style.SUCCESS,
            title="Tournament Created",
            description="\n".join([
                f"Name: `{tourney.dict['sendou']['name']}`",
                f"Sendou.ink ID: `{sendou_id}`",
                f"Tournament Type: `{cls.TYPE}`",
                f"Registration Closes: `{tourney.reg_closes_at()}`"
            ])))

    @classmethod
    async def get_sendou_id(cls, ui):
        """Create a new tournament."""
        directions = "\n".join([
            "Enter the sendou.ink tournament id (`1234`).",
            "It's the number in the tournament url: `sendou.ink/to/1234`."
        ])
        ui.embed.description = directions
        reply = await ui.get_reply()
        if not reply.content.strip().isdigit():
            raise utils.exc.CommandCancel(
                title="Invalid tournament id",
                description="The id must be a number, taken from the `sendou.ink/to/<id>` url.")
        return int(reply.content.strip())
