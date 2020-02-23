"""$to"""
import discord

from offthedialbot import utils


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Command tools for managing tournaments."""
    await utils.Alert(ctx, utils.Alert.Style.INFO, title="`$to`", description="This command group contains many tools for managing tournaments.")