"""$signup"""
from contextlib import contextmanager, asynccontextmanager

import discord

from offthedialbot import utils
from offthedialbot.commands.profile import Profile
from offthedialbot.commands.profile.create import ProfileCreate
from offthedialbot.commands.profile.update import ProfileUpdate


class Signup(utils.Command):
    """ Sign up for the upcoming tournament!

    Or check your dashboard if you already signed up.
    """

    @classmethod
    @utils.deco.otd_only
    async def main(cls, ctx):
        """Sign up for the upcoming tournament!"""
        if (profile := utils.profile.find(ctx.author.id, meta=True)).get_reg() is False:
            await cls.sign_up(ctx, profile)
        else:
            await cls.dashboard(ctx)

    @classmethod
    async def sign_up(cls, ctx, profile):
        """Sign up for the upcoming tournament!"""
        tourney = await cls.check_prerequisites(ctx, profile)

        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(color=utils.colors.COMPETING))
        checklist = cls.Checklist(ui, {
            "prerequisites": True,
            "accepted rules": False,
            "profile is up-to-date": False,
            "smash.gg integration": False,
            "final confirmation": False
        })

        # Check requirements
        with checklist.checking("accepted rules"):
            await cls.accepted_rules(ui, tourney['type'])
        with checklist.checking("profile is up-to-date"):
            profile = await cls.profile_uptodate(ui, profile)
        with checklist.checking("smash.gg integration"):
            await cls.smashgg(ui, profile, tourney['type'])
        with checklist.checking("final confirmation"):
            await cls.confirm_signup(ui)

        await cls.finalize_signup(ui, profile)
        await ui.end(True)

    @classmethod
    async def dashboard(cls, ctx):
        """Show an attendee dashboard to the user."""
        tourney = utils.tourney.get()
        status, tourneygg = await utils.smashgg.post(utils.smashgg.startat)
        if status != 200:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title=f"Status Code - `{status}`", description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
            raise utils.exc.CommandCancel

        start_at = utils.time.datetime.utcfromtimestamp(tourneygg['data']['tournament']['startAt'])
        tourney_data = {
            "name": tourneygg['data']['tournament']['name'],
            "date": start_at.strftime('%A, %B %d | `%I:%M%p` `UTC`'),
            "countdown": start_at - utils.time.datetime.now(),
            "checkin": ('\u2705' if utils.roles.has(ctx.author, "Checked In") else '\u26a0') if tourney['checkin'] else utils.emojis.lock[tourney['checkin']],
            "reg": tourney['reg']
        }
        embed = await cls.create_dashboard_embed(ctx, tourney_data)
        ui: utils.CommandUI = await utils.CommandUI(ctx, embed)
        await ui.get_valid_reaction(['\u2611'], cancel=False)
        await ui.end(True)

    @classmethod
    async def create_dashboard_embed(cls, ctx, tourney):
        """Create dashboard embed from tournament data."""
        embed = discord.Embed(color=utils.colors.COMPETING, title=f"Welcome, {ctx.author.display_name} to your signup dashboard!")
        if tourney['countdown'].total_seconds() <= 0:
            embed.description = "\U0001f3c6 __**The tournament has commenced!**__"
        embed.add_field(name="\U0001f4dd Currently signed up for:", value=f"{tourney['name']}", inline=False)
        embed.add_field(name="\u23f0 Tournament Date:", value=f"{tourney['date']}")
        if tourney['countdown'].total_seconds() > 0:
            embed.add_field(name="Countdown:", value=", ".join([
                f"Days: `{tourney['countdown'].days}`",
                f"Hours: `{int(tourney['countdown'].seconds / 60**2)}:{int(tourney['countdown'].seconds / 60 % 60)}`",
            ]))
        embed.add_field(name="\U0001f4ca Tournament Stats:", value="\n".join([
            f"Registration: {utils.emojis.lock[tourney['reg']]}",
            f"Check-in: {tourney['checkin']}"
        ]), inline=False)
        return embed

    @classmethod
    async def dropout(cls, ui: utils.CommandUI):
        """User requests to dropout."""
        async with ui.create_temp_alert(utils.Alert.Style.WARNING, title="Are you sure you want to dropout?", description="If you are sure, type `dropout` to confirm.") as alert:
            reply = await ui.get_valid_message(lambda m: m.content == 'dropout', {"title": "Unable to confirm.", "description": "Please type `dropout` to confirm."}, cancel=False)
        await ui.end(True, title="Dropout request submitted", description="Your request has been sent to a TO and will be dealt with soon.")

    @classmethod
    async def share(cls, ui):
        """User requests to dropout."""

    @classmethod
    async def check_prerequisites(cls, ctx, profile):
        """Check to make sure the user fits all the prerequisites."""
        tourney = utils.tourney.get()

        check = {
            (lambda: not tourney or tourney["reg"] is False): "Registration is not open.",
            (lambda: profile and profile.get_banned()):
                "You are currently banned from competing in Off the Dial tournaments.",
        }
        if any(values := [value for key, value in check.items() if key()]):
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Registration Failed.", description=values[0])
            raise utils.exc.CommandCancel

        return tourney

    @classmethod
    async def accepted_rules(cls, ui, tourney_type):
        """Make sure the user has accepted the tournament rules."""
        ui.embed.title = f"Read over the rules at **<{utils.tourney.rules[tourney_type]}>**."
        ui.embed.description = "Once finished, select \u2705. By proceeding, you accept and agree to the rules."
        await ui.get_valid_reaction(["\u2705"])

    @classmethod
    async def profile_uptodate(cls, ui, profile):
        """Make sure the user's has a profile, and it is updated."""
        if not isinstance(profile, utils.Profile):
            ui.embed.title = "A profile is required to compete. To create one and proceed, select \u2705."
            ui.embed.description = "Your profile will be saved for future use."
            await ui.get_valid_reaction(["\u2705"])
            await ui.run_command(ProfileCreate.main)
        else:
            await cls.profile_updated(ui, profile)

        return utils.Profile(ui.ctx.author.id)

    @classmethod
    async def profile_updated(cls, ui, profile):
        """Make sure the user's profile is updated."""
        emojis = {
            "check": "\u2705",
            "pencil": "\u270f\ufe0f"
        }
        ui.embed.title = "Is your profile up-to-date?"
        ui.embed.description = f"Select {emojis['check']} if it is, or select {emojis['pencil']} to update it."
        async with cls.show_preview(ui.ctx, profile):
            reply = await ui.get_valid_reaction(list(emojis.values()))
        if reply.emoji == emojis["pencil"]:
            await ui.run_command(ProfileUpdate.main)

    @classmethod
    @asynccontextmanager
    async def show_preview(cls, ctx, profile):
        """Show a preview for profile update."""
        preview = None
        try:
            embed = Profile.create_status_embed(ctx.author.display_name, profile, True)
            embed.title, embed.description = "Preview:", f"**{embed.title}**"
            preview = await ctx.send(embed=embed)
            yield
        finally:
            if preview:
                await preview.delete()

    @classmethod
    async def smashgg(cls, ui, profile, tourney_type):
        """Make sure the user has signed up on smash.gg."""
        # Uses OAuth2 to link user's smash.gg account
        # Give signup code to sign up on smash.gg
        ui.embed.title = f"Sign up on smash.gg at **<{utils.tourney.links[tourney_type]}/register>**."
        ui.embed.description = "Once finished, enter the confirmation code you recieved in the email.\nFor example: `#F1PN28`."
        code = await ui.get_valid_message(r"^#?([A-Fa-f0-9]){6}$",
            {"title": "Invalid Confirmation Code", "description": "The code you entered was not valid, please try again."},
            timeout=600)
        if not code.content.startswith("#"):
            code.content = f"#{code.content}"
        profile.set_reg('code', code.content.upper())

    @classmethod
    async def confirm_signup(cls, ui):
        """Confirm user signup."""
        confirm = utils.Alert.create_embed(utils.Alert.Style.WARNING, "Confirm Signup",
            "Are you ready to sign up? You will not be able to undo without first contacting the organisers.")
        ui.embed.title, ui.embed.description, ui.embed.color = confirm.title, confirm.description, confirm.color
        await ui.get_valid_reaction(["\u2705"])

    @classmethod
    async def finalize_signup(cls, ui, profile: utils.Profile):
        """Finalize user signup, hand out roles, update profile, etc."""
        # Hand out competing role
        await ui.ctx.author.add_roles(utils.roles.get(ui.ctx, "Competing"))

        # Set profile to competing
        profile.set_reg()
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
