"""$to export"""
import json
import csv
import asyncio
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
            if collection in ["signups", "subs"]:
                if collection == "signups":
                    stream = tourney.signups(ignore_ended=True)
                elif collection == "subs":
                    stream = tourney.subs(ignore_ended=True)
                sgg_attendees = await cls.query_attendees(ctx, tourney)

                # Create exportable signups list
                signups = await cls.list_signups(ctx, ui, stream, sgg_attendees)
                # Create & send file from signups list
                file = cls.create_file(signups, collection)
                await ctx.send(file=file)

                # Get list of invalid attendees
                invalid_sgg = cls.list_attendees(sgg_attendees.values())
                invalid_checkin = cls.list_attendees([f"<@{s['id']}>" for s in signups if not s["checked_in"]])

                # Create * send success embed
                embed = discord.Embed(
                    title=":incoming_envelope: *Exporting attendees complete!*",
                    description="Download the spreadsheet below. \U0001f4e5")
                embed.add_field(
                    name="Invalid Attendees - Only on smash.gg:",
                    value=invalid_sgg if invalid_sgg else "✨ No invalid attendees!")
                if discord.utils.get(ctx.guild.roles, name="Checked In"):
                    embed.add_field(
                        name="Invalid Attendees - Not checked in:",
                        value=invalid_checkin if invalid_checkin else "✨ No invalid attendees!")
            elif collection == "overlays":
                embed = await cls.overlays(ctx)
            else:
                raise utils.exc.CommandCancel(
                    title="Unknown export option",
                    description="Option must be either `signups`, `subs`, or `overlays`")
        await ui.end(embed)

    @classmethod
    async def overlays(cls, ctx):
        # Build teams list
        team_roles = []
        signed_up_role = None
        for role in ctx.guild.roles:
            if role.color == discord.Color(utils.colors.COMPETING):
                if role.name != "Signed Up!":
                    team_roles.append(role)
                else:
                    signed_up_role = role
        # Raise error if there are no team roles
        if len(team_roles) <= 0:
            return utils.Alert.create_embed(utils.Alert.Style.DANGER,
                title="No team roles detected",
                description=f"Check that you have given players their team roles, and that the roles are the exact same color as <@&{signed_up_role.id}>.")
        # Build export dictionary
        async def igns(role):
            igns = []
            for member in role.members:
                user = utils.User(member.id)
                igns.append(user.dict["profile"]["ign"])
            return igns
        export = {
            team_role.name: await igns(team_role)
            for team_role in team_roles
        }
        # Send file
        file = StringIO()
        json.dump({"teams": export}, file)
        file.seek(0)
        await ctx.send(file=discord.File(file, filename=f"loadedData.json"))

        # Return export
        return discord.Embed(
            title=":incoming_envelope: *Exporting overlays data complete!*",
            description="Download the json file. \U0001f4e5")

    @staticmethod
    async def list_signups(ctx, ui, signups, sgg_attendees):
        """Return a list with parsed signups."""
        async def per_doc(i, doc):
            # Get base data
            try:
                signup = doc.to_dict()
                user = utils.User(doc.id)

                # Get discord data
                user_discord = user.discord(ctx.guild)
                if user_discord:
                    discord_username = f"{user_discord.name}#{user_discord.discriminator}"
                    checked_in = bool(discord.utils.get(getattr(user_discord, "roles", []), name="Checked In"))
                else:
                    discord_username = "?"
                    checked_in = "N/A"

                # Give export a preview
                if i % 10 == 0:
                    if user_discord:
                        mention = user_discord.mention
                    else:
                        mention = f"`{doc.id}`"
                    ui.embed.clear_fields()
                    ui.embed.add_field(name="Currently exporting:", value=f"> {mention}")
                    await ui.update()

                # get smash.gg
                smashgg = sgg_attendees.pop(user.dict["profile"]["smashgg"][-8:], None)

                # Return final exportable dict
                return {
                    "user": user.dict,
                    "signup": signup,
                    "id": doc.id,
                    "mention": f'<@{doc.id}>',
                    "discord_username": discord_username,
                    "gamerTag": smashgg,
                    "userSlug": user.dict["profile"]["smashgg"][-8:],
                    "elo": user.get_elo(),
                    "checked_in": checked_in
                }
            except:
                raise utils.exc.CommandCancel("Faulty signup", "\n".join([
                    f"Something went wrong while processing one of the signups",
                    f"> `  Mention:` **<@{str(doc.id)}>**",
                    f"> `       ID:` **`{str(doc.id)}`**",
                    f"> ` Username:` **`{discord_username}`**",
                ]))

        return [await per_doc(i, doc) for i, doc in enumerate(signups)]

    @classmethod
    def create_file(cls, signups, collection="signups"):
        # Create fields
        fields = {
            "Discord Mention":   lambda s: s["discord_username"],
            "IGN":               lambda s: s["user"]["profile"]["ign"],
            "SW":                lambda s: s["user"]["profile"]["sw"],
            "Peak Rank":         lambda s: s["user"]["profile"]["rank"],
            "Weapon Pool":       lambda s: s["user"]["profile"]["weapons"],
            "Competitive Exp":   lambda s: s["user"]["profile"]["cxp"],
            "Signal Strength":   lambda s: s["user"]["meta"]["signal"],
            "Smash.gg userSlug": lambda s: s["userSlug"],
            "Smash.gg gamerTag": lambda s: s["gamerTag"],
            "Signup Date":       lambda s: s["signup"]["signupDate"],
            "Modified Date":     lambda s: s["signup"]["modifiedDate"],
            "Timezone":          lambda s: s["signup"]["timezone"],
            "Rank ELO":          lambda s: s["elo"],
            "Checked In":        lambda s: s["checked_in"],
            "Discord ID":        lambda s: s["mention"]
        }
        field_keys = list(fields.keys())
        field_values = list(fields.values())

        # Create signup rows
        signup_rows = []
        for signup in signups:
            signup_rows.append([func(signup) for func in field_values])
        signup_rows.sort(key=lambda row: row[field_keys.index("Signup Date")])

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
