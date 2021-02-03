"""$to sub"""
import discord

from offthedialbot import utils


class ToSub(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, reported: discord.User, sub: discord.User):
        """Automatically handle replacing a reported player with a sub."""
        tourney = utils.Tournament()
        reported_member = ctx.guild.get_member(reported.id)
        sub_member = ctx.guild.get_member(sub.id)
        reported_signup = utils.User(reported.id).signup()
        sub_signup = utils.User(sub.id).signup()

        if not reported_signup or reported_signup.col != "signups":
            raise utils.exc.CommandCancel(
                title="Reported player is invalid",
                description=f"<@{reported.id}> was not found in `signups`.")
        if not sub_signup or sub_signup.col != "subs":
            raise utils.exc.CommandCancel(
                title="Sub player is invalid",
                description=f"<@{sub.id}> was not found in `subs`.")

        # Start database operation
        batch = utils.db.batch()
        # Delete reported_signup
        batch.delete(reported_signup.ref)
        # Move sub_sigunp from subs collection to signups collection
        batch.set(tourney.signups(col=True).document(sub_signup.id), sub_signup.dict)
        batch.delete(sub_signup.ref)
        # Commit database operation. Firebase functions automatically handle signup role
        batch.commit()

        # Bot moves team role from reported player to sub.
        team_role = discord.utils.find(
            lambda r: (
                r.color == discord.Color(utils.colors.COMPETING) and
                r.name != "Signed Up!"),
            reported_member.roles)
        await reported_member.remove_roles(team_role)
        await sub_member.add_roles(team_role)

        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Substitution complete",
            description="\n".join([
                f"Successfully replaced <@{reported.id}> with <@{sub.id}>.",
                "",
                "Reply to the report with this message:",
                "> ```",
                f"> <@{reported.id}> > <@{sub.id}>",
                "> ```"
            ]))
