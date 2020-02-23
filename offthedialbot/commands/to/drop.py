"""$to drop"""
import discord

from offthedialbot import utils


@utils.deco.to_only
async def main(ctx):
    """Drop a player from competing."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Player drop.", description="Send a mention of the player."))

    reply = await ui.get_reply()
    for member in reply.mentions:
        try:
            profile = utils.Profile(member.id)
        except utils.Profile.NotFound:
            profile = None
            await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Failed", description=f"`{member.display_name}` does not own a profile.")
        else:
            if profile.get_competing():
                link = utils.dbh.get_tourney_link()
                ui.embed.description = f"Remove `{member.display_name}` from smash.gg at **<{link}/attendees>**, then hit the \u2705."
                await ui.get_reply("reaction_add", valid_reactions=["\u2705"])
                profile.set_competing(False)
                utils.dbh.update_profile(profile.dict(), member.id)
                await member.remove_roles(utils.roles.competing(ctx.bot))
                await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Complete", description=f"`{member.display_name}` is no longer competing.")
            else:
                await utils.Alert(ctx, utils.Alert.Style.WARNING, title="Drop Failed", description=f"`{member.display_name}` is not competing.")
    
    await ui.end(None)
