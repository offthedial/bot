"""$to attendees"""
from offthedialbot import utils


@utils.deco.to_only
@utils.deco.tourney()
async def main(ctx):
    """Command tools for managing attendees."""
