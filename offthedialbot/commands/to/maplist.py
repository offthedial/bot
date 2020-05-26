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
        else:
            brackets = cls.get_brackets(result)

        maplist = utils.Maplist(await cls.get_maplist(ctx), brackets)
        mode_names = {
            "sz": "Splat Zones",
            "tc": "Tower Control",
            "rm": "Rainmaker",
            "cb": "Clam Blitz"
        }
        phases = cls.get_phases(brackets)
        previous_phase = None
        for (i, game), current_phase in zip(enumerate(maplist.generate()), phases):
            phase_name = list(brackets.keys())[current_phase]
            if previous_phase != current_phase:
                phase_i = i
                await ctx.send(f"__**{phase_name}:**__")
            previous_phase = current_phase
            message = []
            message.append(f"> __{phase_name} Round {i-phase_i+1}:__")
            for mode, stage in game:
                message.append(f"> `{mode_names[mode]}:` {stage}")
            await ctx.send("\n".join(message))

    @classmethod
    async def get_maplist(cls, ctx, index=0):
        """Send a post request to get the maplists from the sendou.ink gql api."""
        request = {"query": "query {\nmaplists {\nsz\ntc\nrm\ncb\n}\n}"}
        async with utils.session.post("https://sendou.ink/graphql", json=request) as resp:
            if resp.status != 200:
                await utils.Alert(ctx, utils.Alert.Style.DANGER, title=f"Status Code - `{resp.status}`", description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
                raise utils.exc.CommandCancel
            return (await resp.json())["data"]["maplists"][index]

    @classmethod
    def get_brackets(cls, result):
        return {
            phase["name"]: [
                node["bestOf"] for node in phase["phaseGroups"]["nodes"][0]["rounds"]
            ] for phase in result["data"]["tournament"]["events"][0]["phases"]
        }

    @classmethod
    def get_phases(cls, brackets):
        phases = []
        for i, games in enumerate(brackets.values()):
            for _ in range(len(games)):
                phases.append(i)
        return phases