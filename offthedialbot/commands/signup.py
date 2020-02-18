"""$signup"""
import discord

from offthedialbot import utils


async def main(ctx):
    """Sign up for the upcoming tournament!"""
    link, profile = await check_prerequisites(ctx)

    ui: utils.CommandUI = await utils.CommandUI(
        ctx,
        discord.Embed(
            title=f"Signup Form",
            color=utils.colors.Roles.COMPETING
    ))

    await profile_updated(ui)
    await smashgg(ui, link)

    await confirm_signup(ui)
    await finalize_signup(ui, profile)
    
    await ui.end(True)


async def check_prerequisites(ctx):
    """Check to make sure the user fits all the prerequisites."""
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

    return link, profile


async def profile_updated(ui):
    """Make sure the user's profiles are up-to-date."""
    ui.embed.description = "Ensure your profile is up-to-date. You can update it with `$profile update`."
    await ui.get_reply('reaction_add', valid_reactions=["\u2705"])


async def smashgg(ui, link):
    """Make sure the user has signed up on smash.gg."""
    # Uses OAuth2 to link user's smash.gg account
    # Give signup code to sign up on smash.gg
    ui.embed.description = f"Sign up on smash.gg at **<{link}>**.\nOnce you are finished, enter your confirmation code you recieved in the email (`#F1PN28`)."
    code = await ui.get_valid_message(r"^#?([A-Za-z0-9]){6}$", {"title": "Invalid Confirmation Code", "description": "The code you entered was not valid, please try again."})
    # Save code to show in exported profiles


async def confirm_signup(ui):
    """Confirm user signup."""
    confirm = utils.Alert.create_embed(utils.Alert.Style.WARNING, "Confirm Signup", "Are you ready to sign up? You will not be able to undo without first contacting the organisers.")
    ui.embed.title, ui.embed.description, ui.embed.color = confirm.title, confirm.description, confirm.color
    await ui.get_reply('reaction_add', valid_reactions=["\u2705"])


async def finalize_signup(ui, profile):
    """Finalize user signup, hand out roles, update profile, etc."""
    # Hand out competing role
    if competing_role := utils.roles.competing(ui.ctx.bot):
        await ui.ctx.author.add_roles(competing_role)

    # Set profile to competing
    profile = utils.Profile(utils.dbh.find_profile(ui.ctx.author.id))
    profile.set_competing(True)
    utils.dbh.update_profile(profile.dict(), ui.ctx.author.id)
