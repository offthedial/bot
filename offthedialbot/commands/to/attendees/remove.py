"""$to attendees remove"""
import discord

from offthedialbot import utils
from offthedialbot import log


@utils.deco.to_only
@utils.deco.tourney()
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Remove attendees.", description="Mention each attendee you want to remove."))
    reply = await ui.get_reply()

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await check_valid_attendee(ctx, attendee)):
            continue
        
        # Remove attendee from smash.gg
        link = utils.dbh.get_tourney()["link"]
        ui.embed.description = f"Remove `{attendee.display_name}` from smash.gg at **<{link}/attendees>**, then hit the \u2705."
        await ui.get_reply("reaction_add", valid_reactions=["\u2705"])
        # Set profile to false
        profile.set_competing(False)
        profile.write()
        # Remove roles
        await attendee.remove_roles(utils.roles.competing(ctx.bot))
        
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Remove attendee complete", description=f"`{attendee.display_name}` is no longer competing.")
    await ui.end(None)


async def check_valid_attendee(ctx, attendee):
        try:
            profile = utils.Profile(attendee.id)
        except utils.Profile.NotFound:
            profile = None
        check = {
            (lambda: not profile): f"`{attendee.display_name}` does not own a profile.",
            (lambda: not profile or not profile.get_competing()): f"`{attendee.display_name}` is not competing."
        }
        if any(values := [value for key, value in check.items() if key()]):
            await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Registration Failed.", description=values[0])
            return False

        return profile