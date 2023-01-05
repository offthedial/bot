"""$to close"""
import json
from urllib.parse import urlparse, parse_qs
import asyncio
from io import StringIO

import discord

from offthedialbot import utils


class ToMaplist(utils.Command):
    @classmethod
    @utils.deco.require_role("Staff")
    async def main(
        cls, ctx, map_pools: str = "", overlays: bool = False
    ):
        """Generate tournament maplist."""
        brackets = await cls.query_brackets(ctx)
        pools = cls.parse_map_pool_link(map_pools)
        maplist = utils.Maplist(pools, brackets)
        generated = maplist.generate()
        async with ctx.typing():
            await cls.display_maplist(ctx, brackets, generated)
        if overlays:
            await ctx.author.send(file=cls.overlays(brackets, generated))
            await ctx.author.send(
                embed=discord.Embed(
                    title=":incoming_envelope: *Exporting overlays data complete!*",
                    description="Download the json file. \U0001f4e5",
                )
            )

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
        try:
            status, result = await utils.graphql(
                "smashgg", query, {"slug": tourney.dict["slug"]}, ctx=ctx
            )
            return {
                phase["name"]: [
                    node["bestOf"] for node in phase["phaseGroups"]["nodes"][0]["rounds"]
                ]
                for phase in result["data"]["tournament"]["events"][0]["phases"]
            }
        except Exception:
            raise utils.exc.CommandCancel(title="Start.gg Error", description="There was an error fetching the brackets from start.gg")

    @classmethod
    async def query_pool(cls, ctx, name=None):
        """Send a post request to get the maplist pool from the sendou.ink gql api."""
        query = f'query {{\nmaplists(name: "{name if name else "LUTI Season X"}") {{\nsz\ntc\nrm\ncb\n}}\n}}'
        status, resp = await utils.graphql("sendou", query, ctx=ctx)
        if not resp["data"]["maplists"]:
            raise utils.exc.CommandCancel(
                title="Invalid maplist name",
                description="Check to make sure you didn't make any typos, or that the maplist doesn't exist.",
            )
        return resp["data"]["maplists"][0]

    @classmethod
    def parse_map_pool_link(cls, sendou_link):
        """Parse map pool share link from sendou.ink or maps.iplabs.ink."""
        all_maps = [
            "Scorch Gorge",
            "Eeltail Alley",
            "Hagglefish Market",
            "Undertow Spillway",
            "Mincemeat Metalworks",
            "Hammerhead Bridge",
            "Museum d'Alfonsino",
            "Mahi-Mahi Resort",
            "Inkblot Art Academy",
            "Sturgeon Shipyard",
            "MakoMart",
            "Wahoo World",
            "Flounder Heights",
            "Brinewater Springs"
        ]
        try:
            params = parse_qs(urlparse(sendou_link).query)
            # Convert url query parameter to dictionary
            pool = {
                value.split(":")[0]: value.split(":")[1]
                for value in params["pool"][0].split(";")
            }
            # Replace each value with a list of each map
            for key, value in pool.items():
                # Convert hex to binary string (cut off leading 0b1)
                binary = str(bin(int(value, 16)))[3:]
                # Build map pool by looping over each digit
                maps = []
                for i in range(len(binary)):
                    if binary[i] == "1":
                        maps.append(all_maps[i])
                # Replace pool value with map pool
                pool[key] = maps
            return pool
        except:
            raise utils.exc.CommandCancel(title="Map pool error", description="Map pool link was badly formed, double-check that it follows the [IPL map pool specification](https://github.com/IPLSplatoon/IPLMapGen2/blob/splat3/url-serialization-docs.md).")

    @classmethod
    async def display_maplist(cls, ctx, brackets, maplist):
        mode_names = {
            "sz": "<:sz:804107770328383558> `Splat Zones`",
            "tc": "<:tc:804107769242058783> `Tower Control`",
            "rm": "<:rm:804107768130306078> `Rainmaker`",
            "cb": "<:cb:804107767601168394> `Clam Blitz`",
        }
        # Get phases
        phases = [
            i for i, games in enumerate(brackets.values()) for _ in range(len(games))
        ]
        previous_phase = None
        phase_i = None
        # Loop over all phases
        for (i, game), current_phase in zip(enumerate(maplist), phases):
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
            await asyncio.sleep(0.2)

    @classmethod
    def overlays(cls, brackets, maplist):
        mode_names = {
            "sz": "Splat Zones",
            "tc": "Tower Control",
            "rm": "Rainmaker",
            "cb": "Clam Blitz",
        }
        export = {}
        # Get phases
        phases = [
            i for i, games in enumerate(brackets.values()) for _ in range(len(games))
        ]
        previous_phase = None
        phase_i = None
        # Loop over all phases
        for (i, game), current_phase in zip(enumerate(maplist), phases):
            phase_name = list(brackets.keys())[current_phase]
            # New phase
            if previous_phase != current_phase:
                phase_i = i
            previous_phase = current_phase
            # Send round message
            export[f"{phase_name} Round {i-phase_i+1}"] = [
                {"map": map, "mode": mode_names[mode]} for mode, map in game
            ]
        # Send file
        file = StringIO()
        json.dump({"rounds": export}, file)
        file.seek(0)
        return discord.File(file, filename=f"loadedData.json")
