"""$to attendees remove"""
import discord

from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Remove attendees.", description="Mention each attendee you want to remove.", color=utils.colors.COMPETING))
    reply = await ui.get_valid_message(lambda m: len(m.mentions) == 1, {"title": "Invalid Message", "description": "Make sure to send a **mention** of the attendee."})

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee)):
            continue
        
        await remove_smashgg(ui, attendee)
        await remove_attendee(ctx, attendee, profile, reason=f"attendee manually removed by {ctx.author.display_name}.")

        # Complete ban
        profile.write()
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Remove attendee complete", description=f"`{attendee.display_name}` is no longer competing.")
    
    await ui.end(None)


async def remove_smashgg(ui, attendee):
    """Remove attendee from smash.gg."""
    link = utils.dbh.get_tourney()["link"]
    ui.embed.description = f"Remove `{attendee.display_name}` from smash.gg at **<{link}/attendees>**, then hit the \u2705."
    await ui.get_reply("reaction_add", valid_reactions=["\u2705"])


async def check_valid_attendee(ctx, attendee):
    """Check if the attendee is valid or not."""
    try:
        profile = utils.Profile(attendee.id)
    except utils.Profile.NotFound:
        profile = None
    check = {
        (lambda: not profile): f"`{attendee.display_name}` does not own a profile.",
        (lambda: not profile or not profile.get_competing()): f"`{attendee.display_name}` is not competing."
    }
    if any(values := [value for key, value in check.items() if key()]):
        await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Removal Failed.", description=values[0])
        return False

    return profile


async def remove_attendee(ctx, attendee, profile, *, reason="attendee isn't competing anymore."):
    """Remove competing from attendee's profile and discord roles."""
    profile.set_competing(False)  # Profile
    if attendee:  # Roles
        await attendee.remove_roles(*[utils.roles.get(ctx, name=name) for name in ["Competing", "Checked In"]], reason=reason)
