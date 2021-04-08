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
            # Get tourney signups and smash.gg signups
            tourney = utils.Tournament()
            if collection != "subs":
                stream = tourney.signups(ignore_ended=True)
            else:
                stream = tourney.subs(ignore_ended=True)
            sgg_attendees = await cls.query_attendees(ctx, tourney)

            # Create exportable signups list
            signups = cls.list_signups(ctx, stream, sgg_attendees)
            # Create & send file from signups list
            file = cls.create_file(signups, collection)
            await ctx.send(file=file)

            # Get list of invalid attendees
            invalid_sgg = cls.list_attendees(sgg_attendees.values())
            invalid_checkin = cls.list_attendees([f"<@{s['id']}>" for s in signups if not s["checked_in"]])

            # Create * send success embed
            if collection != "subs":
                embed = discord.Embed(
                    title=":incoming_envelope: *Exporting attendees complete!*",
                    description="Download the spreadsheet below. \U0001f4e5")
                embed.add_field(
                    name="Invalid Attendees - Only on smash.gg:",
                    value=invalid_sgg if invalid_sgg else "✨ No invalid attendees!")
                embed.add_field(
                    name="Invalid Attendees - Not checked in:",
                    value=invalid_checkin if invalid_checkin else "✨ No invalid attendees!")
        await ui.end(embed)

    @staticmethod
    def list_signups(ctx, signups, sgg_attendees):
        """Return a list with parsed signups."""
        def per_doc(doc):
            # Get base data
            signup = doc.to_dict()
            user = utils.User(doc.id)
            # Get discord and smash.gg
            user_discord = user.discord(ctx.guild)
            smashgg = sgg_attendees.pop(user.dict["profile"]["smashgg"], None)

            # Calculate cxp
            cxp = int({
                "This is my first tournament :0": 0,
                "I've played in one or two tournaments.": 2,
                "I've played in some tournaments.": 5,
                "I've played in a lot of tournaments.": 10,
            }[user.dict["profile"]["cxp"]["amount"]] + (user.dict["profile"]["cxp"]["placement"]**(1/3)))
            # Calculate discord data
            if user_discord:
                discord_username = f"{user_discord.name}#{user_discord.discriminator}"
                checked_in = bool(discord.utils.get(getattr(user_discord, "roles", []), name="Checked In"))
            else:
                discord_username = "-"
                checked_in = "N/A"

            # Return final exportable dict
            return {
                **user.dict,
                **signup,
                "id": doc.id,
                "mention": f'<@{doc.id}>',
                "discord_username": discord_username,
                "smashgg": {
                    "gamerTag": smashgg,
                    "slug": user.dict["profile"]["smashgg"]
                },
                "stylepoints": {
                    "sup-agg": user.dict["profile"]["stylepoints"]["aggressive"],
                    "obj-sla": user.dict["profile"]["stylepoints"]["slayer"],
                    "anc-mob": user.dict["profile"]["stylepoints"]["mobile"],
                    "fle-foc": user.dict["profile"]["stylepoints"]["focused"],
                },
                "elo": user.get_elo(),
                "tzOffset": signup["tzOffset"] / 60,
                "cxp": cxp,
                "checked_in": checked_in
            }

        return [per_doc(doc) for doc in signups]

    @classmethod
    def create_file(cls, signups, collection="signups"):
        # Create fields
        fields = {
            "Discord Mention":          lambda s: s["discord_username"],
            "Smash.gg gamerTag":        lambda s: s["smashgg"]["gamerTag"],
            "IGN":                      lambda s: s["profile"]["ign"],
            "SW":                       lambda s: s["profile"]["sw"],
            "Cumulative ELO":           lambda s: s["elo"],
            "SZ":                       lambda s: s["profile"]["ranks"]["sz"],
            "TC":                       lambda s: s["profile"]["ranks"]["tc"],
            "RM":                       lambda s: s["profile"]["ranks"]["rm"],
            "CB":                       lambda s: s["profile"]["ranks"]["cb"],
            "support < aggressive":     lambda s: s["stylepoints"]["sup-agg"],
            "objective < slayer":       lambda s: s["stylepoints"]["obj-sla"],
            "anchor < mobile":          lambda s: s["stylepoints"]["anc-mob"],
            "flex < focused":           lambda s: s["stylepoints"]["fle-foc"],
            "Competitive Experience":   lambda s: s["cxp"],
            "Signal Strength":          lambda s: s["meta"]["signal"],
            "Timezone Offset (hours)":  lambda s: s["tzOffset"],
            "Confirmation Code":        lambda s: s["confirmationCode"],
            "Checked In":               lambda s: s["checked_in"],
            "Smash.gg user slug":       lambda s: s["smashgg"]["slug"],
            "Discord ID":               lambda s: s["mention"]
        }
        field_keys = list(fields.keys())
        field_values = list(fields.values())

        # Create signup rows
        signup_rows = []
        for signup in signups:
            signup_rows.append([func(signup) for func in field_values])
        signup_rows.sort(key=lambda row: row[field_keys.index("Confirmation Code")])

        # Write file
        file = StringIO()
        writer: csv.writer = csv.writer(file)
        writer.writerows([field_keys, []] + signup_rows)
        file.seek(0)
        # Create discord attachment
        return discord.File(file, filename=f"{collection}.csv")

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
    def list_attendees(cls, attendees):
        """Display in a list, all invalid attendees."""
        return "\n".join(f"`-` {value}" for value in attendees)
