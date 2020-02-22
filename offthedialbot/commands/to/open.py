"""$to open"""
import discord

from offthedialbot import utils


@utils.deco.to_only
@utils.deco.registration(required=False)
async def main(ctx):
    """Open registration for a new tournament!"""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Opening registration for a new tournament...", color=utils.colors.Roles.COMPETING))
    
    # Steps
    await link(ui)

    await ui.end(True)


async def link(ui):
    """Set the smash.gg link for the next tournament."""
    ui.embed.description = "Enter the new link to the tournament. (https://smash.gg/slug)"
    ui.embed.add_field(name="Link:", value=f"~~`{str(utils.dbh.get_tourney_link())}`~~")
    reply = await ui.get_reply()
    utils.dbh.set_tourney_link(reply.content)
    ui.embed.set_field_at(0, name="Link:", value=f"`{str(utils.dbh.get_tourney_link())}`")
