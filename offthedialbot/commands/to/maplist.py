"""$to close"""
from urllib.parse import urlparse, parse_qs
import asyncio

from offthedialbot import utils


class ToMaplist(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, map_pools: str = ""):
        """Generate tournament maplist."""
        brackets = await cls.query_brackets(ctx)
        if not map_pools.startswith("https://sendou.ink/maps"):
            pools = await cls.query_pool(ctx, map_pools)
        else:
            pools = cls.parse_sendou_link(map_pools)
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
        status, result = await utils.graphql("smashgg", query, {"slug": tourney.dict["slug"]}, ctx=ctx)
        return {
            phase["name"]: [
                node["bestOf"] for node in phase["phaseGroups"]["nodes"][0]["rounds"]
            ] for phase in result["data"]["tournament"]["events"][0]["phases"]
        }


    @classmethod
    async def query_pool(cls, ctx, name=None):
        """Send a post request to get the maplist pool from the sendou.ink gql api."""
        query = f'query {{\nmaplists(name: "{name if name else "LUTI Season X"}") {{\nsz\ntc\nrm\ncb\n}}\n}}'
        status, resp = await utils.graphql("sendou", query, ctx=ctx)
        if not resp["data"]["maplists"]:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Invalid maplist name", description="Check to make sure you didn't make any typos, or that the maplist doesn't exist.")
            raise utils.exc.CommandCancel
        return resp["data"]["maplists"][0]

    @classmethod
    def parse_sendou_link(cls, sendou_link):
        """Parse sendou.ink map pool share link."""
        params = parse_qs(urlparse(sendou_link).query)
        pools = {
            "sz": [],
            "tc": [],
            "rm": [],
            "cb": [],
        }
        for key, value in params.items():
            for mode in value.pop().split(","):
                pools[mode.lower()].append(key)
        return pools

    @classmethod
    async def display_maplist(cls, ctx, brackets, maplist):
        mode_names = {
            "sz": "<:sz:804107770328383558> `Splat Zones`",
            "tc": "<:tc:804107769242058783> `Tower Control`",
            "rm": "<:rm:804107768130306078> `Rainmaker`",
            "cb": "<:cb:804107767601168394> `Clam Blitz`"
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
