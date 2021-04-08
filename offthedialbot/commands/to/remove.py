"""$to remove"""
import discord

from offthedialbot import utils


class ToRemove(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, reported: discord.User, sub: discord.User = None):
        """Automatically handle removing a reported player and optionally replacing them with a sub."""
        tourney = utils.Tournament()
        smashgg_link = f"[smash.gg](https://smash.gg/tournament/{tourney.dict['slug']})"

        # Start database operation
        batch = utils.db.batch()

        # Get reported player
        reported_member = ctx.guild.get_member(reported.id)
        reported_signup = utils.User(reported.id).signup()
        if not reported_signup:
            raise utils.exc.CommandCancel(
                title="Reported player is invalid",
                description=f"<@{reported.id}> was not found.")
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title="\u200b",
            description=f"Remove `{await reported_signup.smashgg()}` from {smashgg_link}")

        # Get team role
        team_role = discord.utils.find(lambda r: (
                r.color == discord.Color(utils.colors.COMPETING) and
                r.name != "Signed Up!"),
            getattr(reported_member, "roles", []))

        # Get reported sub, if necessary
        if sub:
            # Check if reported has a team role
            if not team_role:
                raise utils.exc.CommandCancel(
                    title="No team role",
                    description=f"<@{reported.id}> does not have a team role.")
            # Check if sub player is valid
            sub_member = ctx.guild.get_member(sub.id)
            sub_signup = utils.User(sub.id).signup()
            if not sub_signup or sub_signup.col != "subs":
                raise utils.exc.CommandCancel(
                    title="Sub player is invalid",
                    description=f"<@{sub.id}> was not found in `subs`.")
            # Bot moves team role from reported player to sub.
            await reported_member.remove_roles(team_role)
            await sub_member.add_roles(team_role)
            # Alert smash.gg removal
            await utils.Alert(ctx, utils.Alert.Style.INFO,
                title="\u200b",
                description=f"Add `{await sub_signup.smashgg()}` to {smashgg_link} on team `{team_role.name}`.")
            # Move sub_signup from subs collection to signups collection
            batch.delete(reported_signup.ref)
            batch.set(tourney.signups(col=True).document(sub_signup.id), sub_signup.dict)
            batch.delete(sub_signup.ref)
            # Set success message
            message = "\n".join([
                f"Successfully removed <@{reported.id}>, replaced by <@{sub.id}>.",
                "",
                "Reply to the report with this message:",
                "> ```",
                f"> <@{reported.id}> > <@{sub.id}>",
                "> ```"
            ])

        else:
            # Check if reported has a team role
            if team_role:
                await reported_member.remove_roles(team_role)
            # Delete reported_signup
            batch.delete(reported_signup.ref)
            # Set success message
            message = f"Successfully removed <@{reported.id}>."

        # Commit database operation. Firebase functions automatically handle signup role
        batch.commit()
        # Success message
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Player Removal Complete",
            description=message)
