"""$to attendees add"""
import discord

from offthedialbot import utils
from . import check_valid_attendee


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(
            title="Add attendees.",
            description="Mention each attendee you want to add.",
            color=utils.colors.COMPETING))

    reply = await ui.get_valid_message(lambda m: len(m.mentions) >= 1,
        {"title": "Invalid Mention", "description": "Make sure to send a **mention** of the attendee."})

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee)):
            continue

        profile.set_competing(True)
        profile.write()
        if attendee:  # Roles
            await attendee.add_roles(
                *[utils.roles.get(ctx, name) for name in ["Competing", "Checked In"] if utils.roles.get(ctx, name)],
                reason="Fixing a code mistake"
            )

        # Complete ban
        await ui.create_alert(utils.Alert.Style.SUCCESS,
            title="Remove attendee complete",
            description=f"`{attendee.display_name}` is no longer competing.")

    await ui.end(None)
