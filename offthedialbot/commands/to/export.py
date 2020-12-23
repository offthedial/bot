"""$to export"""
import csv
from io import StringIO

from offthedialbot.utils import smashgg
import discord
import json

from pprint import pprint

from offthedialbot import utils


class ToExport(utils.Command):
    """ Export signups
    """

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Temporary export signups command."""
        ui: utils.CommandUI = await utils.CommandUI(ctx,
            discord.Embed(title="Exporting attendees...", color=utils.colors.COMPETING))
        async with ctx.typing():
            file = await cls.export_attendees(ctx)

        await ui.end(True,
            title=":incoming_envelope: *Exporting attendees complete!*",
            description="Download the spreadsheet below. \U0001f4e5")
        await ctx.send(file=file)

    @classmethod
    async def export_attendees(cls, ctx):
        """Poop."""
        db = utils.firestore.db
        cls.fix_stylepoints(db)

        docs = db.collection(u'tournaments').document(u'2KnLtpnPNjz2AE0OxwX5').collection(u'signups').stream()
        query = """
            query getAllParticipants($slug: String) {
                tournament(slug: $slug) {
                    participants(query:{perPage:999}) {
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
        status, data = await utils.smashgg.post(query, "it-s-dangerous-to-go-alone-december-2020", ctx)
        if status != 200:
            await ctx.send("error lol: " + status)
            await ctx.send(f"```json\n{data}\n```")
            raise utils.exc.CommandCancel

        nodes = data["data"]["tournament"]["participants"]["nodes"]
        smashgg_attendee_slugs = [node["user"]["slug"][5:] for node in nodes]


        async def per_doc(doc):
            signup = doc.to_dict()
            user = db.collection(u'users').document(doc.id).get().to_dict()
            powers = [utils.Profile.convert_rank_power(rank) for rank in user["profile"]["ranks"].values()]
            elo = round(sum(powers) / len(powers), 1)
            smashgg = False
            if user["profile"]["smashgg"] in smashgg_attendee_slugs:
                smashgg = [node for node in nodes if node["user"]["slug"][5:] == user["profile"]["smashgg"]][0]
                smashgg = {
                    "gamerTag": smashgg["gamerTag"],
                    "slug": smashgg["user"]["slug"][5:]
                }
                smashgg_attendee_slugs.remove(user["profile"]["smashgg"])

            discorduser = ctx.bot.get_user(int(doc.id))

            return {
                "id": doc.id,
                "discord_username": f"{discorduser.name}#{discorduser.discriminator}" if discorduser else "None",
                **signup,
                **user,
                "elo": elo,
                "smashgg": smashgg
            }

        full_signups = [await per_doc(doc) for doc in docs]
        not_on_otd = "\n".join([f'> `-` {node["gamerTag"]}' for node in nodes if node["user"]["slug"][5:] in smashgg_attendee_slugs])

        await ctx.send(file=cls.create_file(full_signups))
        await ctx.send(f"Signed up on smash.gg but not otd.ink: \n{not_on_otd}")

    @classmethod
    def create_file(cls, full_signups):
        file = StringIO()
        writer: csv.writer = csv.writer(file)
        csv_profiles = []

        for full_signup in full_signups:
            csv_profiles.append([
                full_signup["discord_username"],
                full_signup["smashgg"]["gamerTag"] if full_signup["smashgg"] else None,
                full_signup["profile"]["ign"],
                full_signup["profile"]["sw"],
                full_signup["profile"]["ranks"]["sz"],
                full_signup["profile"]["ranks"]["tc"],
                full_signup["profile"]["ranks"]["rm"],
                full_signup["profile"]["ranks"]["cb"],
                full_signup["elo"],
                full_signup["profile"]["stylepoints"]["support"],
                full_signup["profile"]["stylepoints"]["aggressive"],
                full_signup["profile"]["stylepoints"]["objective"],
                full_signup["profile"]["stylepoints"]["slayer"],
                full_signup["profile"]["stylepoints"]["anchor"],
                full_signup["profile"]["stylepoints"]["mobile"],
                full_signup["profile"]["stylepoints"]["flex"],
                full_signup["profile"]["stylepoints"]["focused"],
                full_signup["profile"]["cxp"]["amount"],
                full_signup["profile"]["cxp"]["placement"],
                full_signup["meta"]["signal"],
                full_signup["tzOffset"],
                full_signup["confirmationCode"],
                full_signup["smashgg"]["slug"] if full_signup["smashgg"] else None,
                f'<@{full_signup["id"]}>'
            ])
        csv_profiles.sort(key=lambda row: row[7])

        writer.writerows([[
            "Discord Mention","Smash.gg gamerTag", "IGN", "SW", "SZ", "TC", "RM", "CB", "Cumulative ELO",
            "support", "aggressive", "objective", "slayer", "anchor", "mobile", "flex", "focused",
            "Amount of tourneys", "highest teams placed above", "Signal Strength", "Timezone Offset (minutes)", "Confirmation Code", "Smash.gg user slug", "Discord ID"], []] + csv_profiles)
        file.seek(0)
        return discord.File(file, filename="signups.csv")


    @classmethod
    def fix_stylepoints(cls, db):
        batch = db.batch()
        docs = db.collection(u'users').stream()
        for doc in docs:
            if "stylepoints" in doc.to_dict()["profile"].keys():
                stylepoints = doc.to_dict()["profile"]["stylepoints"]
                print(stylepoints)
                ref = db.collection(u'users').document(doc.id)
                batch.update(ref, {
                    u"profile.stylepoints.support": abs(stylepoints["aggressive"] - 10),
                    u"profile.stylepoints.objective": abs(stylepoints["slayer"] - 10),
                    u"profile.stylepoints.anchor": abs(stylepoints["mobile"] - 10),
                    u"profile.stylepoints.flex": abs(stylepoints["focused"] - 10),
                })
                print(doc.to_dict()["profile"]["stylepoints"])
            else:
                print(f"Skipped empty profile: {doc.id}")
        batch.commit()
