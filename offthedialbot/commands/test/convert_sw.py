"""$test convert_sw"""
import discord

from offthedialbot import utils


async def main(ctx):
    """Cycle through each of the different alert types."""
    profiles = utils.dbh.profiles.find({}, {"_id": True, "status.SW": True});
    for profile in profiles:
        utils.dbh.profiles.update_one({"_id": profile["_id"]}, {'$set': {'status.SW': str(profile["status"]["SW"])}})