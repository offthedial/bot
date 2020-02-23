"""$to attendees"""
from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Command tools for managing attendees."""
