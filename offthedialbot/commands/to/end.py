"""$to end"""
import discord

from offthedialbot import utils


async def main(ctx):
    """Cycle through each of the different alert types."""
    profiles = utils.dbh.profiles.find({"meta.competing": True}, {"_id": True})
    for p in profiles:
        await ctx.bot.OTD.get_member(p["_id"]).remove_roles(utils.roles.competing(ctx.bot))
        utils.dbh.profiles.update_one({"_id": p["_id"]}, {"$set": {"meta.competing": False}})
