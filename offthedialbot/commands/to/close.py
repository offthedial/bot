"""$to close"""
import discord
from offthedialbot import utils
from .attendees import export


@utils.deco.to_only
async def main(ctx):
    """Close registration for the tournament."""
    if not utils.dbh.get_tourney_link():
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Close Failed", description="Tournament isn't open to begin with!")
        raise utils.exc.CommandCancel

    ui = await utils.CommandUI(ctx, discord.Embed(title="Closing registration for the tournament...", color=utils.colors.Roles.COMPETING))
    # Steps
    utils.dbh.set_tourney_link(None)
    await export.export_profiles(ui, {"meta.competing": True})
