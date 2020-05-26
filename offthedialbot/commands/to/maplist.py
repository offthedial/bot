"""$to close"""
import discord

from offthedialbot import utils


class ToMaplist(utils.Command):
    """Create and send a maplist."""

    @classmethod
    @utils.deco.require_role("Organiser")
    @utils.deco.tourney()
    async def main(cls, ctx):
        status, result = await utils.smashgg.post(utils.smashgg.totalgames)
        if status != 200:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title=f"Status Code - `{status}`", description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
            raise utils.exc.CommandCancel

        brackets = {phase["name"]: [node["totalGames"] for node in phase["sets"]["nodes"]] for phase in result["data"]["tournament"]["events"][0]["phases"]}
        maplist = utils.Maplist(brackets)
        mode_names = {
            "sz": "Splat Zones",
            "tc": "Tower Control",
            "rm": "Rainmaker",
            "cb": "Clam Blitz"
        }
        round_names = []
        for name, games in brackets.items():
            for i in range(len(games)):
                round_names.append(name)

        message = []
        for (i, game), round_name in zip(enumerate(maplist.generate()), round_names):
            message.append(f"\n__{round_name} Round {i+1}__")
            for mode, stage in game:
                message.append(f"`{mode_names[mode]}:` {stage}")

        await ctx.send("\n".join(message))
