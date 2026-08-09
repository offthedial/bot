"""$to export"""
import json
import csv
import datetime, pytz
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
            # Get tourney signups
            tourney = utils.Tournament()
            if collection in ["signups", "subs"]:
                if collection == "signups":
                    stream = tourney.signups(ignore_ended=True)
                elif collection == "subs":
                    stream = tourney.subs(ignore_ended=True)

                # Create exportable signups list
                signups = await cls.list_signups(ctx, ui, stream)
                # Create & send file from signups list
                file = cls.create_file(signups, collection)
                await ctx.send(file=file)

                # Get list of invalid attendees
                invalid_checkin = cls.list_attendees([f"<@{s['id']}>" for s in signups if not s["checked_in"]])
                diff = await cls.diff_players(ctx, tourney, signups) if collection == "signups" else None

                # Create * send success embed
                embed = discord.Embed(
                    title=":incoming_envelope: *Exporting attendees complete!*",
                    description="Download the spreadsheet below. \U0001f4e5")
                if diff:
                    for name, ids in zip(
                        ["On sendou.ink only", "Not on sendou.ink", "No sendou.ink account"], diff
                    ):
                        invalid = cls.list_attendees([f"<@{id}>" for id in ids])
                        embed.add_field(
                            name=f"Invalid Attendees - {name}:",
                            value=invalid if invalid else "✨ No invalid attendees!")
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
        # Build teams list from sendou, rather than from the discord team roles
        # that are themselves derived from it
        tourney = utils.Tournament()
        teams = await utils.sendou.teams(tourney.dict["sendouId"], ctx=ctx)
        if not teams:
            return utils.Alert.create_embed(utils.Alert.Style.DANGER,
                title="No teams detected",
                description=f"No teams are registered on {tourney.sendou_link} yet.")
        # Build export dictionary
        def build_team_data(team):
            members = []
            for m in team["members"]:
                # A player can be on a sendou team without an otd.ink profile,
                # so fall back to the names sendou already gave us
                profile = (utils.User(m["discordId"]).dict or {}).get("profile", {})
                members.append({
                    "splashtag": profile.get("splashtag") or m["inGameName"] or m["name"],
                    "weapons": profile.get("weapons", [])
                })
            return members
        export = {
            team["name"]: build_team_data(team)
            for team in teams
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
    async def list_signups(ctx, ui, signups):
        """Return a list with parsed signups."""
        async def per_doc(i, doc):
            user = utils.User(doc.id)
            sendou_link = await user.sendou_link()

            # Get base data
            try:
                signup = doc.to_dict()

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

                # get timezone
                timezone = f"UTC{datetime.datetime.now(pytz.timezone(signup['timezone'])).strftime('%z')} ({signup['timezone']})"

                # Return final exportable dict
                return {
                    "user": user.dict,
                    "signup": signup,
                    "rank": user.get_rank(),
                    "rank_sort": user.get_sortable_rank(),
                    "weapons": user.get_weapons(),
                    "timezone": timezone,
                    "sendou": sendou_link or "",
                    "id": doc.id,
                    "mention": f'<@{doc.id}>',
                    "discord": discord_username,
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
    async def diff_players(cls, ctx, tourney, signups):
        teams = await utils.sendou.teams(tourney.dict["sendouId"], ctx=ctx)
        if not teams:
            return None

        theirs = {m["discordId"] for team in teams for m in team["members"]}
        ours = {s["id"] for s in signups}
        linked = {s["id"] for s in signups if s["sendou"]}

        unmatched, no_account = [], []
        for id in sorted(ours - theirs):
            (unmatched if id in linked else no_account).append(id)

        return sorted(theirs - ours), unmatched, no_account

    @classmethod
    def create_file(cls, signups, collection="signups"):
        # Create fields
        fields = {
            "Discord Mention":   lambda s: s["discord"],
            "SplashTag":         lambda s: s["user"]["profile"]["splashtag"],
            "Sendou.ink":        lambda s: s["sendou"],
            "SW":                lambda s: s["user"]["profile"]["sw"],
            "Parsed Rank":       lambda s: s["rank"],
            "Sortable Rank":     lambda s: s["rank_sort"],
            "Weapon Pool":       lambda s: s["weapons"],
            "Competitive Exp":   lambda s: s["user"]["profile"]["cxp"],
            "Signal Strength":   lambda s: s["user"]["meta"]["signal"],
            "Timezone":          lambda s: s["timezone"],
            "Signup Date":       lambda s: s["signup"]["signupDate"],
            "Modified Date":     lambda s: s["signup"]["modifiedDate"],
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
    def list_attendees(cls, attendees):
        """Display in a list, all invalid attendees."""
        content = "\n".join(f"`-` {value}" for value in attendees)
        if len(content) > 2000:
            return f"🚫 Too many!! ({len(attendees)})"
        return content
