"""$to end"""
import discord

from offthedialbot import utils


async def main(ctx):
    """End the tournament."""
    await ctx.trigger_typing()
    utils.dbh.set_tourney_link(None)  # Remove the tourney link
    # Update all the profiles
    profiles = utils.dbh.profiles.find({"meta.competing": True}, {"_id": True})
    for p in profiles:
        # Remove competing role
        await ctx.bot.OTD.get_member(p["_id"]).remove_roles(utils.roles.competing(ctx.bot))
        # Set competing key to false
        utils.dbh.profiles.update_one({"_id": p["_id"]}, {"$set": {"meta.competing": False}})
    await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Tournament Complete!", description="All roles have been removed, profiles have been updated, and signal strength has been applied.")
