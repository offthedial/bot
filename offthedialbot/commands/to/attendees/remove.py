"""$to attendees remove"""
import discord

from offthedialbot import utils
from offthedialbot import log


@utils.deco.to_only
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Remove attendees.", description="Mention each attendee you want to remove."))
    reply = await ui.get_reply()

    for member in reply.mentions:

        # Check to make sure the attendee is valid
        try:
            profile = utils.Profile(profile)
        except utils.Profile.NotFound:
            await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Remove attendee failed", description=f"`{member.display_name}` does not own a profile.")
            continue
        else:
            if not profile.is_competing():
                await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Remove attendee failed", description=f"`{member.display_name}` is not competing.")
                continue
        
        # Remove attendee from smash.gg
        link = utils.dbh.get_tourney_link()
        ui.embed.description = f"Remove `{member.display_name}` from smash.gg at **<{link}/attendees>**, then hit the \u2705."
        await ui.get_reply("reaction_add", valid_reactions=["\u2705"])
        # Set profile to false
        profile.set_competing(False)
        utils.dbh.update_profile(profile.dict(), member.id)
        # Remove roles
        await member.remove_roles(utils.roles.competing(ctx.bot))
        
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Remove attendee complete", description=f"`{member.display_name}` is no longer competing.")
    await ui.end(None)
