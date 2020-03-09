"""$signup"""
from contextlib import contextmanager

import discord

from offthedialbot import utils
from offthedialbot.commands.profile import create, update


@utils.deco.otd_only
async def main(ctx):
    """Sign up for the upcoming tournament!"""
    link, profile = await check_prerequisites(ctx)

    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(color=utils.colors.COMPETING))
    checklist = Checklist(ui, {
        "prerequisites": True,
        "profile is updated": False,
        "smash.gg integration": False,
        "final confirmation": False
    })

    # Check requirements
    with checklist.checking("profile is updated"):
        profile = await profile_updated(ui, profile)
    with checklist.checking("smash.gg integration"):
        await smashgg(ui, link)
    with checklist.checking("final confirmation"):
        await confirm_signup(ui)

    await finalize_signup(ui, profile)
    
    await ui.end(True)


async def check_prerequisites(ctx):
    """Check to make sure the user fits all the prerequisites."""
    link = utils.dbh.get_tourney()["link"] if utils.dbh.get_tourney() else None
    try:
        profile = utils.Profile(ctx.author.id)
    except utils.Profile.NotFound:
        profile = None

    check = {
        (lambda: not link): "Registration is not open.",
        (lambda: profile and profile.get_banned()): "You are currently banned from competing in Off the Dial tournaments.",
        (lambda: profile and profile.get_competing()): "You are already signed up!"
    }
    if any(values := [value for key, value in check.items() if key()]):
        await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Registration Failed.", description=values[0])
        raise utils.exc.CommandCancel

    return link, profile


async def profile_updated(ui, profile):
    """Make sure the user's profiles are up-to-date."""
    if not profile:
        ui.embed.title = "A profile is required to compete. To create one and proceed, select \u2705."
        await ui.get_valid_reaction(["\u2705"])
        await ui.run_command(create.main)
    else:
        ui.embed.title = "Is your profile up-to-date? Select \u2705 if it is, or select \u270f\ufe0f to update it."
        reply = await ui.get_valid_reaction(["\u2705", "\u270f\ufe0f"])
        if reply.emoji == "\u270f\ufe0f":
            await ui.run_command(update.main)
    return utils.Profile(ui.ctx.author.id)


async def smashgg(ui, link):
    """Make sure the user has signed up on smash.gg."""
    # Uses OAuth2 to link user's smash.gg account
    # Give signup code to sign up on smash.gg
    ui.embed.title = f"Sign up on smash.gg at **<{link}/register>**."
    ui.embed.description = "Once finished, enter the confirmation code you recieved in the email (`#F1PN28`)."
    code = await ui.get_valid_message(r"^#?([A-Za-z0-9]){6}$", {"title": "Invalid Confirmation Code", "description": "The code you entered was not valid, please try again."}, timeout=540)
    # Save code to show in exported profiles


async def confirm_signup(ui):
    """Confirm user signup."""
    confirm = utils.Alert.create_embed(utils.Alert.Style.WARNING, "Confirm Signup", "Are you ready to sign up? You will not be able to undo without first contacting the organisers.")
    ui.embed.title, ui.embed.description, ui.embed.color = confirm.title, confirm.description, confirm.color
    await ui.get_valid_reaction(["\u2705"])


async def finalize_signup(ui, profile):
    """Finalize user signup, hand out roles, update profile, etc."""
    # Hand out competing role
    await ui.ctx.author.add_roles(utils.roles.get(ui.ctx, "Competing"))

    # Set profile to competing
    profile.set_competing(True)
    profile.write()


class Checklist:
    """Set checklist field on the signup form."""

    emojis = {
        True: '\u2705',
        None: '\U0001f7e6',
        False: '\u2b1b'
    }

    def __init__(self, ui, checklist):
        self.ui = ui
        self.checklist = checklist
        
        self.ui.embed.add_field(name="Requirements:", value=self.create(self.checklist))

    @contextmanager
    def checking(self, field):
        """Check a requirement as a context manager.""" 
        try:
            self.update({field: None})
            yield
        finally:
            self.update({field: True})

    def update(self, updates):
        """Update the checklist inside of the UI."""
        self.checklist.update(**updates)
        self.ui.embed.set_field_at(0, name=self.ui.embed.fields[0].name, value=self.create(self.checklist))

    @classmethod
    def create(cls, checklist):
        """Create the checklist string."""
        return "\n".join(f"{cls.emojis[value]} Checking {name}..." for name, value in checklist.items())
    