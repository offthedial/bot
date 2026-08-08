"""$to remove"""
import discord

from offthedialbot import utils


class ToRemove(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, reported: discord.User, sub: discord.User = None):
        """Automatically handle removing a reported player and optionally replacing them with a sub."""
        tourney = utils.Tournament()

        # Start database operation
        batch = utils.db.batch()

        # Get reported player
        reported_member = ctx.guild.get_member(reported.id)
        reported_signup = utils.User(reported.id).signup()
        if not reported_signup:
            raise utils.exc.CommandCancel(
                title="Reported player is invalid",
                description=f"<@{reported.id}> was not found.")

        # Check if sub player is valid, before anything is mutated on sendou
        if sub:
            sub_member = ctx.guild.get_member(sub.id)
            sub_signup = utils.User(sub.id).signup()
            if not sub_signup or sub_signup.col != "subs":
                raise utils.exc.CommandCancel(
                    title="Sub player is invalid",
                    description=f"<@{sub.id}> was not found in `subs`.")

        # Take them off their team on sendou.ink
        team, member = await utils.sendou.find_team(tourney.dict["sendouId"], reported.id, ctx=ctx)
        result = await utils.sendou.remove_member(
            tourney.dict["sendouId"], team["id"], member["userId"]
        ) if team else (404, "Not on a team")
        await cls.alert(ctx, result,
            f"Removed `{reported_signup.splashtag()}` from sendou.ink.",
            f"Remove `{reported_signup.splashtag()}` from {tourney.sendou_link} manually.")

        # Get team role
        team_role = discord.utils.find(lambda r: (
                r.color == discord.Color(utils.colors.COMPETING) and
                r.name != "Signed Up!"),
            getattr(reported_member, "roles", []))

        # Get reported sub, if necessary
        if sub:
            if team_role:
                # Bot moves team role from reported player to sub.
                await reported_member.remove_roles(team_role)
                await sub_member.add_roles(team_role)
                team_name = team_role.name
            else:
                team_name = None
            # Put the sub on the same team on sendou.ink
            team_name = team["name"] if team else team_name
            sub_id = await utils.sendou.user_id(sub.id)
            result = await utils.sendou.add_member(
                tourney.dict["sendouId"], team["id"], sub_id
            ) if team and sub_id else (404, "No team or sendou.ink account")
            await cls.alert(ctx, result,
                f"Added `{sub_signup.splashtag()}` to team `{team_name}`.",
                f"Add `{sub_signup.splashtag()}` to {tourney.sendou_link} on team `{team_name}` manually.")
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

    @classmethod
    async def alert(cls, ctx, result, done, manual):
        """Alert the result of a sendou.ink roster change.

        Sendou blocks removing a team owner or anyone who has already played a
        set, so a refusal is expected rather than exceptional - fall back to
        asking staff to do it by hand instead of cancelling the command.
        """
        status, error = result
        if status in (200, 204):
            return await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="​", description=done)
        await utils.Alert(ctx, utils.Alert.Style.WARNING,
            title=f"Sendou.ink refused - `{status}`", description=f"{manual}\n> `{error}`")
