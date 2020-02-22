"""$to start"""
import discord

from offthedialbot import utils


@utils.deco.to_only
@utils.deco.tourney(False)
async def main(ctx):
    """Start the tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Commencing tournament...", color=utils.colors.Roles.COMPETING))
    await ui.end(True)
