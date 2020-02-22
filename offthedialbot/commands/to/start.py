"""$to start"""
import discord

from offthedialbot import utils


@utils.deco.to_only
@utils.deco.registration(required=False)
async def main(ctx):
    """Start the tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Commencing tournament..."))
    await ui.end(True)
