"""$to drop"""
import discord

from offthedialbot import utils
from offthedialbot import log


async def main(ctx):
    """Drop a player from competing."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Player drop.", description="Send a mention of the player."))

    reply = await ui.get_reply()
    for member in reply.mentions:
        if profile := utils.dbh.find_profile(member.id):
            profile = utils.Profile(profile)
            if profile.is_competing():
                link = utils.dbh.get_tourney_link()
                ui.embed.description = f"Remove player from smash.gg at **<{link}>**, then hit the \u2705."
                await ui.get_reply("reaction_add", valid_reactions=["\u2705"])
                profile.set_competing(False)
                utils.dbh.update_profile(profile.dict(), member.id)
                await member.remove_roles(utils.roles.competing(ctx.bot))
                await ui.end(True)
            else:
                await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Drop Failed", description=f"`{member.display_name}` is not competing.")
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Drop Failed", description=f"`{member.display_name}` does not own a profile.")
    
    await ui.end(None)
