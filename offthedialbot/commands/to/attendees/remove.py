"""$to attendees remove"""
import discord

from offthedialbot import utils
from . import attendee_and_profile, check_valid_attendee


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(
            title="Remove attendees.",
            description="Mention or send an ID of each attendee you want to remove.",
            color=utils.colors.COMPETING)
    )
    reply = await ui.get_reply()
    attendees = reply.mentions
    for id in reply.content.split():
        try:
            attendees.append(await ctx.bot.fetch_user(int(id)))
        except ValueError:
            continue

    if not attendees:
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="No valid attendees found.", description="There were no valid attendees in your message.")
        raise utils.exc.CommandCancel

    for attendee in attendees:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee)):
            continue

        await from_smashgg(ui, attendee)
        await from_competing(ctx, attendee, profile, reason=f"attendee manually removed by {ctx.author.display_name}.")

        # Complete removal
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Remove attendee complete",
            description=f"`{attendee.display_name}` is no longer competing.")

    await ui.end(None)


async def disqualified(ctx, **kwargs):
    """Remove attendees who have not checked in."""
    for attendee, profile in attendee_and_profile(ctx):
        checks: list = [{
            "left": (
                lambda a, p: a is None,
                "attendee left the server"),
            "checkin": (
                lambda a, p: not utils.roles.has(a, "Checked In"),
                "attendee failed to check-in"),

        }[key] for key in kwargs.keys()]
        disq = [(check, reason) for check, reason in checks if check(attendee, profile)]

        if any(disq):
            await from_competing(ctx, attendee, profile, reason=disq[0][1])


async def from_competing(ctx, attendee, profile: utils.ProfileMeta, *, reason="attendee isn't competing anymore."):
    """Remove competing from attendee's profile and discord roles."""
    # Profile
    profile.set_reg(value=False)
    profile.set_reg("code", None)
    profile.write()
    if attendee:  # Roles
        await attendee.remove_roles(
            *[utils.roles.get(ctx, name) for name in ["Competing", "Checked In"] if utils.roles.get(ctx, name)],
            reason=reason
        )


async def from_smashgg(ui, attendee):
    """Remove attendee from smash.gg."""
    link = utils.tourney.get_tourney()["link"].split("/")[-1]
    ui.embed.description = f"Remove `{attendee.display_name}` from smash.gg at **<https://smash.gg/admin/tournament/{link}/attendees>**, then hit the \u2705."
    await ui.get_valid_reaction(["\u2705"])
