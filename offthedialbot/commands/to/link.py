"""$to link"""
import discord

from offthedialbot import utils


async def main(ctx):
    """Set the smash.gg link for the next tournament."""
    emojis = {
        "edit": "\u270f\ufe0f",
        "remove": "\U0001f5d1\ufe0f"
    }
    embed = discord.Embed(title="Current Tournament Listing", description=f"React with {emojis['edit']} to edit and {emojis['remove']} to remove.", color=utils.colors.Roles.DIALER)
    embed.add_field(name="Link:", value=f"`{str(utils.dbh.get_tourney_link())}`")
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    reply = await ui.get_reply("reaction_add", valid_reactions=list(emojis.values()))

    if reply.emoji == emojis['edit']:
        embed.description = "Enter the new link to the tournament. (https://smash.gg/slug)"
        embed.set_field_at(0, name="Link:", value=f"~~`{str(utils.dbh.get_tourney_link())}`~~")
        reply = await ui.get_reply()
        utils.dbh.set_tourney_link(reply.content)
    elif reply.emoji == emojis['remove']:
        utils.dbh.set_tourney_link(link=None)

    await ui.end(True)
