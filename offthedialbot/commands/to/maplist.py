"""$to close"""
import discord
import asyncio

from offthedialbot import utils


class ToMaplist(utils.Command):
    """Create and send a maplist."""

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, pools: dict = None):
        """Generate tournament maplist."""
        brackets = await cls.query_brackets(ctx)
        if not pools:
            pools = await cls.query_pool(ctx)
        maplist = utils.Maplist(pools, brackets)
        async with ctx.typing():
            await cls.display_maplist(ctx, brackets, maplist)

    @classmethod
    async def query_brackets(cls, ctx):
        """Call the smash.gg api on the tournament slug to retrieve the brackets needed."""
        tourney = utils.Tournament()
        query = """query($slug: String) {
          tournament(slug: $slug) {
            events {
              phases {
                name
                phaseGroups {
                  nodes {
                    rounds {
                    	bestOf
                    }
                  }
                }
              }
            }
          }
        }"""
        status, result = await utils.smashgg.post(query, {"slug": tourney.dict["slug"]}, ctx=ctx)
        if status != 200:
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title=f"Status Code: `{str(status)}`",
                description=f"```json\n{result}\n```")
            raise utils.exc.CommandCancel

        return {
            phase["name"]: [
                node["bestOf"] for node in phase["phaseGroups"]["nodes"][0]["rounds"]
            ] for phase in result["data"]["tournament"]["events"][0]["phases"]
        }


    @classmethod
    async def query_pool(cls, ctx, index=0, name=None):
        """Send a post request to get the maplist pool from the sendou.ink gql api."""
        request = {"query": f'query {{\nmaplists(name: "{name if name else "LUTI Season X"}") {{\nsz\ntc\nrm\ncb\n}}\n}}'}
        async with utils.session.post("https://sendou.ink/graphql", json=request) as resp:
            if resp.status != 200:
                await utils.Alert(ctx, utils.Alert.Style.DANGER, title=f"Status Code - `{resp.status}`", description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
                raise utils.exc.CommandCancel
            return (await resp.json())["data"]["maplists"][index]

    @classmethod
    async def display_maplist(cls, ctx, brackets, maplist):
        mode_names = {
            "sz": "<:sz:747322891606950011> `Splat Zones`",
            "tc": "<:tc:747322891749556264> `Tower Control`",
            "rm": "<:rm:747322891703550042> `Rainmaker`",
            "cb": "<:cb:747322891338776588> `Clam Blitz`"
        }
        # Get phases
        phases = [i for i, games in enumerate(brackets.values()) for _ in range(len(games))]
        previous_phase = None
        phase_i = None
        # Loop over all phases
        for (i, game), current_phase in zip(enumerate(maplist.generate()), phases):
            phase_name = list(brackets.keys())[current_phase]
            # Display the phase title, if it's a new phase
            if previous_phase != current_phase:
                phase_i = i
                await ctx.send(f"__**{phase_name}:**__")
            previous_phase = current_phase
            # Send round message
            message = []
            message.append(f"> __{phase_name} Round {i-phase_i+1}:__")
            for mode, stage in game:
                message.append(f"> {mode_names[mode]}: {stage}")
            await ctx.send("\n".join(message))
            # Ensure round messages aren't sent out of order
            await asyncio.sleep(.2)
