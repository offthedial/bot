"""$to end"""
import discord

from offthedialbot import utils


@utils.deco.to_only
@utils.deco.registration(False)
async def main(ctx):
    """End the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed=discord.Embed(title="Ending tournament..."))

    # Steps
    profiles = utils.dbh.profiles.find({"meta.competing": True}, {"_id": True})
    await remove_roles(ui, profiles)
    await update_profiles(ui, profiles)

    await ui.end(True)


async def remove_roles(ui, profiles):
    ui.embed.description = "Removing `competing` role from everyone."
    await ui.update()
    for p in profiles:
        await ui.ctx.bot.OTD.get_member(p["_id"]).remove_roles(utils.roles.competing(ui.ctx.bot))  # Remove competing role

async def update_profiles(ui, profiles):
    ui.embed.description = "Updating profiles to set `competing` to false."
    await ui.update()
    for p in profiles:
        utils.dbh.profiles.update_one({"_id": p["_id"]}, {"$set": {"meta.competing": False}})  # Set competing key to false