"""$to attendees remove"""
import discord

from offthedialbot import utils
from offthedialbot import log


@utils.deco.to_only
async def main(ctx):
    """Remove an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Player drop.", description="Send a mention of the player."))

    reply = await ui.get_reply()
    for member in reply.mentions:
        if profile := utils.dbh.find_profile(member.id):
            profile = utils.Profile(profile)
            if profile.is_competing():
                link = utils.dbh.get_tourney_link()
                ui.embed.description = f"Remove `{member.display_name}` from smash.gg at **<{link}>**, then hit the \u2705."
                await ui.get_reply("reaction_add", valid_reactions=["\u2705"])
                profile.set_competing(False)
                utils.dbh.update_profile(profile.dict(), member.id)
                await member.remove_roles(utils.roles.competing(ctx.bot))
                await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Complete", description=f"`{member.display_name}` is no longer competing.")
            else:
                await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Failed", description=f"`{member.display_name}` is not competing.")
        else:
            await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Failed", description=f"`{member.display_name}` does not own a profile.")
    
    await ui.end(None)
