"""$to attendees remove"""
import discord

from offthedialbot import utils
from . import attendee_and_profile, check_valid_attendee


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Remove attendees.", description="Mention each attendee you want to remove.", color=utils.colors.COMPETING))
    reply = await ui.get_valid_message(lambda m: len(m.mentions) == 1, {"title": "Invalid Mention", "description": "Make sure to send a **mention** of the attendee."})

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee)):
            continue
        
        await from_smashgg(ui, attendee)
        await from_competing(ctx, attendee, profile, reason=f"attendee manually removed by {ctx.author.display_name}.")

        # Complete ban
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Remove attendee complete", description=f"`{attendee.display_name}` is no longer competing.")
    
    await ui.end(None)


async def disqualified(ctx, **kwargs):
    """Remove attendees who have not checked in."""
    for attendee, profile in attendee_and_profile(ctx):
        checks: list = [{
            "left": (lambda a, p: a is None, "attendee left the server"),
            "checkin": (lambda a, p: "Checked In" not in [role.name for role in getattr(attendee, 'roles', [])], "attendee failed to check-in"),
        }[key] for key in kwargs.keys()]

        disq = [(check, reason) for check, reason in checks if check(attendee, profile)]

        if any(disq):
            await from_competing(ctx, attendee, profile, reason=disq[0][1])


async def from_competing(ctx, attendee, profile, *, reason="attendee isn't competing anymore."):
    """Remove competing from attendee's profile and discord roles."""
    # Profile
    profile.set_competing(False)
    # profile.set_cc(None)
    profile.write()
    if attendee:  # Roles
        await attendee.remove_roles(*[utils.roles.get(ctx, name) for name in ["Competing", "Checked In"] if utils.roles.get(ctx, name)], reason=reason)


async def from_smashgg(ui, attendee):
    """Remove attendee from smash.gg."""
    link = utils.dbh.get_tourney()["link"].split("/")[-1]
    ui.embed.description = f"Remove `{attendee.display_name}` from smash.gg at **<https://smash.gg/admin/tournament/{link}/attendees>**, then hit the \u2705."
    await ui.get_valid_reaction(["\u2705"])
