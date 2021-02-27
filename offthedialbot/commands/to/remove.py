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

        # Get reported_signup
        reported_member = ctx.guild.get_member(reported.id)
        reported_signup = utils.User(reported.id).signup()
        if not reported_signup or reported_signup.col != "signups":
            raise utils.exc.CommandCancel(
                title="Reported player is invalid",
                description=f"<@{reported.id}> was not found in `signups`.")
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title="\u200b",
            description=f"Remove `{await reported_signup.smashgg()}` from {smashgg_link}")

        # Get team role
        team_role = discord.utils.find(lambda r: (
                r.color == discord.Color(utils.colors.COMPETING) and
                r.name != "Signed Up!"),
            reported_member.roles)

        # Get reported_sub, if necessary
        if sub:
            sub_member = ctx.guild.get_member(sub.id)
            sub_signup = utils.User(sub.id).signup()
            if not sub_signup or sub_signup.col != "subs":
                raise utils.exc.CommandCancel(
                    title="Sub player is invalid",
                    description=f"<@{sub.id}> was not found in `subs`.")
            await utils.Alert(ctx, utils.Alert.Style.INFO,
                title="\u200b",
                description=f"Add `{await sub_signup.smashgg()}` to {smashgg_link} on team `{team_role.name}`.")

        # Start database operation
        batch = utils.db.batch()
        # Delete reported_signup
        batch.delete(reported_signup.ref)
        if sub:
            # Move sub_sigunp from subs collection to signups collection
            batch.set(tourney.signups(col=True).document(sub_signup.id), sub_signup.dict)
            batch.delete(sub_signup.ref)
        # Commit database operation. Firebase functions automatically handle signup role
        batch.commit()

        # Bot moves team role from reported player to sub.
        await reported_member.remove_roles(team_role)
        if sub:
            await sub_member.add_roles(team_role)
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Player Removal Complete",
            description="\n".join([
                f"Successfully removed <@{reported.id}>, replaced by <@{sub.id}>.",
                "",
                "Reply to the report with this message:",
                "> ```",
                f"> <@{reported.id}> > <@{sub.id}>",
                "> ```"
            ]) if sub else f"Successfully removed <@{reported.id}>.")
