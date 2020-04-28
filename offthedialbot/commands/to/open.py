"""$to open"""
import discord

from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney(0)
async def main(ctx):
    """Open registration for a new tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx,
        discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.COMPETING))

    # Steps
    tourney_type = await get_tourney_type(ui)
    utils.tourney.new(tourney_type)

    await ui.end(True)


async def get_tourney_type(ui):
    """Create a new tournament."""
    directions = f"Enter the tournament type ({', '.join([tourney.name for tourney in utils.tourney.Type])})"
    ui.embed.title = directions
    reply = await ui.get_valid_message(
        lambda r: getattr(utils.tourney.Type, r.content.upper(), False) is not False,
        {'title': 'Invalid Tournament Type', 'description': directions})
    return getattr(utils.tourney.Type, reply.content.upper())
