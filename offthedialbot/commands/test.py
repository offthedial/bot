"""Contains code for $test."""

import discord
from offthedialbot import utils


async def main(ctx, content):
    """$test command."""

    # create embed
    embed = discord.Embed(title=content, description="`IGN:`")
    ui = await utils.CommandUI(ctx, embed)

    # wait for ign
    embed = utils.embeds.create_error_embed(
        error="Invalid IGN", description="**Please type your __IGN__** `(in-game name)`"
    )
    reply = await ui.get_valid_message(r"^.{1,10}$", error_embed=embed)
    ui.embed.add_field(name="ign", value=reply.content)

    # wait for reaction
    reply = await ui.get_reply('reaction_add', valid_reactions=["\U0001f69b", "\u2702"])
    ui.embed.add_field(name="reaction", value=reply[0].emoji)

    # confirm happy
    ui.embed.add_field(name="Is this good?", value="Hit that '\u2705' to say so.", inline=False)
    reply = await ui.get_reply('reaction_add', valid_reactions=['\u2705'])

    # End
    await ui.end(status=True)
