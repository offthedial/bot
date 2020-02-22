"""$to start"""
import discord

from offthedialbot import utils


@utils.deco.to_only
@utils.deco.registration(required=False)
async def main(ctx):
    """Commence the tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Commencing tournament..."))
    # something????
    await ui.end(True)
