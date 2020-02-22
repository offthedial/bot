"""$to attendees"""
from offthedialbot import utils


@utils.deco.to_only
@utils.deco.registration(required=True)
async def main(ctx):
    """Command tools for managing attendees."""
