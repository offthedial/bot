"""$to export"""
import csv
from io import StringIO

import discord

from offthedialbot import utils


class ToExport(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, collection: str = "signups"):
        """Export all of the signups or subs of the most recent tournament."""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Exporting attendees...", color=utils.colors.COMPETING))

        async with ctx.typing():
            tourney = utils.Tournament()
            sgg_attendees = await cls.query_attendees(ctx, tourney)

            if collection != "subs":
                stream = tourney.signups(ignore_ended=True)
            else:
                stream = tourney.subs(ignore_ended=True)

            signups = cls.list_signups(ctx, stream, sgg_attendees)
            file = cls.create_file(signups, collection)

            await ctx.send(file=file)
            if collection != "subs":
                embed = discord.Embed(
                    title=":incoming_envelope: *Exporting attendees complete!*",
                    description="Download the spreadsheet below. \U0001f4e5")
                embed.add_field(
                    name="Invalid Attendees - Only on smash.gg:",
                    value=cls.list_attendees(sgg_attendees.values()))
                embed.add_field(
                    name="Invalid Attendees - Not checked in:",
                    value=cls.list_attendees([f"<@{s.id}>" for s in signups if s["checkedin"]]))
        await ui.end(embed)

    @classmethod
    async def query_attendees(cls, ctx, tourney):
        """Query attendees from smash.gg, return an object containing their gamerTag and user slug."""
        query = """
            query getAllParticipants($slug: String) {
                tournament(slug: $slug) {
                    participants(query:{perPage:500}) {
                        nodes {
                            gamerTag
                            user {
                                slug
                            }
                        }
                    }
                }
            }
        """
        status, data = await utils.graphql("smashgg", query, {"slug": tourney.dict["slug"]}, ctx)
        return {
            node["user"]["slug"][5:]: node["gamerTag"]
            for node in data["data"]["tournament"]["participants"]["nodes"]
        }

    @classmethod
    def list_signups(cls, ctx, signups, sgg_attendees):
        """Return a list with parsed signups."""
        def per_doc(doc):
            signup = doc.to_dict()
            user = utils.User(doc.id)
            smashgg_tag = sgg_attendees.pop(user.dict["profile"]["smashgg"], None)
            discord_user = ctx.bot.get_user(int(doc.id))
            roles = getattr(ctx.guild.get_member(int(doc.id)), "roles", [])

            cxp = int({
                "This is my first tournament :0": 0,
                "I've played in one or two tournaments.": 2,
                "I've played in some tournaments.": 5,
                "I've played in a lot of tournaments.": 10,
            }[user.dict["profile"]["cxp"]["amount"]] + (user.dict["profile"]["cxp"]["placement"]**(1/3)))

            return {
                **user.dict,
                **signup,
                "id": doc.id,
                "discord_username": f"{discord_user.name}#{discord_user.discriminator}" if discord_user else None,
                "elo": user.get_elo(),
                "smashgg": {
                    "gamerTag": smashgg_tag,
                    "slug": user.dict["profile"]["smashgg"]
                },
                "cxp": cxp,
                "stylepoints": {
                    "sup-agg": user.dict["profile"]["stylepoints"]["aggressive"],
                    "obj-sla": user.dict["profile"]["stylepoints"]["slayer"],
                    "anc-mob": user.dict["profile"]["stylepoints"]["mobile"],
                    "fle-foc": user.dict["profile"]["stylepoints"]["focused"],
                },
                "checkedin": bool(discord.utils.get(roles, name="Checked In"))
            }

        return [per_doc(doc) for doc in signups]

    @classmethod
    def create_file(cls, signups, collection="signups"):
        file = StringIO()
        writer: csv.writer = csv.writer(file)
        csv_profiles = []

        for signup in signups:
            csv_profiles.append([
                signup["discord_username"],
                signup["smashgg"]["gamerTag"] if signup["smashgg"] else None,
                signup["profile"]["ign"],
                signup["profile"]["sw"],
                signup["elo"],
                signup["profile"]["ranks"]["sz"],
                signup["profile"]["ranks"]["tc"],
                signup["profile"]["ranks"]["rm"],
                signup["profile"]["ranks"]["cb"],
                signup["stylepoints"]["sup-agg"],
                signup["stylepoints"]["obj-sla"],
                signup["stylepoints"]["anc-mob"],
                signup["stylepoints"]["fle-foc"],
                signup["cxp"],
                signup["meta"]["signal"],
                signup["tzOffset"],
                signup["confirmationCode"],
                signup["checkedin"],
                signup["smashgg"]["slug"] if signup["smashgg"] else None,
                f'<@{signup["id"]}>'
            ])
        csv_profiles.sort(key=lambda row: row[4])
        writer.writerows([[
            "Discord Mention",
            "Smash.gg gamerTag",
            "IGN",
            "SW",
            "Cumulative ELO",
            "SZ",
            "TC",
            "RM",
            "CB",
            "support < aggressive",
            "objective < slayer",
            "anchor < mobile",
            "flex < focused",
            "Competitive Experience",
            "Signal Strength",
            "Timezone Offset (minutes)",
            "Confirmation Code",
            "Checked In",
            "Smash.gg user slug",
            "Discord ID"
        ], []] + csv_profiles)
        file.seek(0)
        return discord.File(file, filename=f"{collection}.csv")

    @classmethod
    def list_attendees(cls, attendees):
        """Display in a list, all invalid attendees."""
        return "\n".join(f"`-` {value}" for value in attendees)
