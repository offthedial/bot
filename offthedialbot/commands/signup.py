"""$signup"""
import discord

from offthedialbot import utils


async def main(ctx):
    """Sign up for the upcoming tournament!"""

    link = utils.dbh.get_tourney_link()
    if profile := utils.dbh.find_profile(id=ctx.author.id):
        profile = utils.Profile(profile)

    check = {
        (lambda: not link): "Registration is not open.",
        (lambda: not profile): "You don't have a profile, create one with `$profile create`.",
        (lambda: not profile or profile.is_banned()): "You are currently banned from competing in Off the Dial tournaments.",
        (lambda: not profile or profile.is_competing()): "You are already signed up!"
    }
    if any(values := [value for key, value in check.items() if key()]):
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Registration Failed.", description=values[0])
        raise utils.exc.CommandCancel

    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title=f"Signup Form"))
    ui.embed.description = "Is your profile is up to date? You can update it with `$profile update`."
    await ui.get_reply('reaction_add', valid_reactions=["\u2705"])

    # Connect smash.gg using OAuth2
    # Give signup code to signup on smash.gg
    # Query those signed up to check if they signed up

    ui.embed.description = f"Register on smash.gg at **<{link}>**.\nOnce you are finished, hit the checkmark."
    await ui.get_reply('reaction_add', valid_reactions=["\u2705"])

    await ctx.author.add_roles(utils.roles.competing(ctx.bot))
    profile = utils.Profile(utils.dbh.find_profile(ctx.author.id))
    profile.set_competing(True)
    utils.dbh.update_profile(profile.dict(), ctx.author.id)

    await ui.end(True)
