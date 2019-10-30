import discord
from offthedialbot import utils


async def main(ctx, content):

    # create embed
    embed = discord.Embed(title=content, description="`IGN:`")
    ui = await utils.CommandUI(ctx, embed)

    # wait for ign
    reply = await ui.get_reply()
    ui.embed.add_field(name="ign", value=reply.content)

    reply = await ui.get_reply('reaction_add', valids=["\U0001f69b", "\u2702"])
    ui.embed.add_field(name="reaction", value=reply[0].emoji)

