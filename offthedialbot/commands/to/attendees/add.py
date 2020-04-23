"""$to attendees add"""
import discord

from offthedialbot import utils
from . import check_valid_attendee


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Add an attendee to the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(
            title="Add attendees.",
            description="Mention each attendee you want to add.",
            color=utils.colors.COMPETING)
    )
    reply = await ui.get_valid_message(lambda m: len(m.mentions) >= 1,
        {"title": "Invalid Mention", "description": "Make sure to send a **mention** of the attendees."})

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee, competing=False)):
            continue

        await on_smashgg(ui, attendee)
        await on_competing(ctx, attendee, profile, reason=f"attendee manually added by {ctx.author.display_name}.")

        # Complete add
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Add attendee complete",
            description=f"`{attendee.display_name}` is now competing.")

    await ui.end(None)


async def on_competing(ctx, attendee, profile: utils.ProfileMeta, *, reason="attendee isn't competing anymore."):
    """Add competing to attendee's profile and discord roles."""
    # Profile
    profile.set_reg()
    profile.write()
    if attendee:  # Roles
        await attendee.add_roles(
            *[utils.roles.get(ctx, name) for name in ["Competing", "Checked In"] if utils.roles.get(ctx, name)],
            reason=reason
        )


async def on_smashgg(ui, attendee):
    """Add attendee on smash.gg."""
    link = utils.dbh.get_tourney()["link"].split("/")[-1]
    ui.embed.description = f"If applicable, add `{attendee.display_name}` to smash.gg at **<https://smash.gg/admin/tournament/{link}/attendees>**, then hit the \u2705."
    await ui.get_valid_reaction(["\u2705"])
