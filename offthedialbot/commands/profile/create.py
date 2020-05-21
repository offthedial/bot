"""$profile create"""
import asyncio
import re

import discord

from offthedialbot import utils
from . import Profile


class ProfileCreate(utils.Command):
    """Create your profile."""

    @classmethod
    @utils.deco.profile_required(reverse=True)
    async def main(cls, ctx):
        """Create your profile."""
        profile: utils.Profile = utils.Profile(ctx.author.id, new=True)

        embed: discord.Embed = Profile.create_status_embed(ctx.author.display_name, profile)
        ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

        profile = await cls.set_user_status(ui, profile)
        ui.embed = cls.create_stylepoints_embed()
        profile.set_stylepoints(await cls.get_user_stylepoints(ui))
        ui.embed = cls.create_cxp_embed()
        profile.set_cxp(await cls.get_user_cxp(ui))
        profile.write()
        await ui.end(True)

    @classmethod
    async def set_user_status(cls, ui: utils.CommandUI, profile: utils.Profile) -> utils.Profile:
        """Get valid message for each rank."""
        for index, key in enumerate(['IGN', 'SW', 'Ranks']):
            cls.clean_status_key(profile, key)

            if key != "Ranks":
                await cls.set_status_field(ui, profile, key, index)
            else:
                await cls.set_rank_field(ui, profile, index)

        if not await cls.confirm_profile(ui):
            profile: utils.Profile = utils.Profile(ui.ctx.author.id, new=True)
            ui.embed = Profile.create_status_embed(ui.ctx.author.display_name, profile)
            profile: utils.Profile = await cls.set_user_status(ui, profile)

        return profile

    @classmethod
    async def set_status_field(cls, ui, profile, key, field_index) -> None:
        """Prompt the user for a standard user profile field."""
        instructions = {"IGN": 'Enter your **IGN**, `(WP*Zada, Lepto)`', "SW": 'Enter your **SW**, `(SW-0000-0000-0000)`'}
        ui.embed.title = instructions[key]
        reply = await ui.get_valid_message(
            valid=lambda m: cls.parse_reply(key, m.content), error_fields={
                "title": f"Invalid {key}",
                "description": instructions[key]
            })
        field_value: str = cls.parse_reply(key, reply.content)
        if key == "IGN":
            profile.set_ign(field_value)
        elif key == "SW":
            profile.set_sw(field_value)
        ui.embed.set_field_at(field_index, name=key, value=Profile.display_field(key, field_value))

    @classmethod
    async def set_rank_field(cls, ui: utils.CommandUI, profile: utils.Profile, field_index: int) -> None:
        """Prompt the user for each of the rank fields."""
        instructions = lambda k: f'Enter your **__{k}__ Rank**, `(C, A-, S+0, X2350.0)`'
        for key in profile.get_ranks().keys():
            ui.embed.title = instructions(key)
            reply: discord.Message = await ui.get_valid_message(
                valid=lambda m: cls.parse_reply("Ranks", m.content),
                error_fields={
                    "title": "Invalid Rank",
                    "description": instructions(key)
                })
            profile.set_rank(key, cls.parse_reply("Ranks", reply.content))
            ui.embed.set_field_at(field_index,
                name="Ranks",
                value=Profile.display_field("Ranks", profile.get_ranks()), inline=False)

    @classmethod
    def clean_status_key(cls, profile: utils.Profile, key: str) -> tuple:
        """Clean status at key, return new value."""
        clean_status = {
            "IGN": None,
            "SW": None,
            "Ranks": {
                "Splat Zones": None,
                "Tower Control": None,
                "Rainmaker": None,
                "Clam Blitz": None,
            },
        }
        profile.profile[key] = clean_status[key]
        return key, profile.profile[key]

    @classmethod
    async def get_user_stylepoints(cls, ui: utils.CommandUI, user_playstyles=None) -> list:
        """Get the user's playstyle and calculate their, style points."""
        if user_playstyles is None:
            user_playstyles: list = []
        while True:
            tasks = [
                asyncio.create_task(ui.get_valid_message(
                    lambda m: m.content.lower() in utils.Profile.playstyles.keys(),
                    {"title": "Invalid Playstyle.", "description": "Please enter a valid playstyle."}, cancel=None)),
                asyncio.create_task(ui.get_valid_reaction(['\u23ed\ufe0f'], cancel=None)),
                await ui.create_cancel_task(),
            ]
            ui.embed.set_field_at(0, name="Playstyles", value=cls.create_playstyle_list(user_playstyles))
            task, reply = await ui.wait_tasks(set(tasks))
            await ui.delete_alert()

            if task == tasks[0]:
                content: str = reply.content.lower()
                if content in user_playstyles:
                    user_playstyles.remove(content)
                else:
                    user_playstyles.append(content)
            elif task == tasks[1]:
                if not user_playstyles:
                    await ui.create_alert(utils.Alert.Style.DANGER,
                        title="No Playstyles Selected",
                        description="You did not select any playstyles.")
                else:
                    break
            else:
                await ui.end(False)

        return user_playstyles

    @classmethod
    async def get_user_cxp(cls, ui: utils.CommandUI) -> int:
        """Get the user's playstyle and calculate their, style points."""
        reply: discord.Message = await ui.get_valid_message(r'^\d+$',
            {"title": "Invalid number.", "description": "Please enter a valid number of tournaments."})
        return int(reply.content)

    @classmethod
    def create_stylepoints_embed(cls) -> discord.Embed:
        """Create embed for asking stylepoints."""
        embed: discord.Embed = discord.Embed(color=utils.colors.DIALER,
            title="Enter all of the playstyles below that apply to you",
            description=f"Re-enter a playstyle to remove it. Click the \u23ed\ufe0f when done.")
        embed.add_field(name="Playstyles", value=cls.create_playstyle_list())
        return embed

    @classmethod
    def create_cxp_embed(cls) -> discord.Embed:
        """Create embed for asking competitive experience."""
        return discord.Embed(color=utils.colors.DIALER,
            title=f"How many tournaments, with at-least 16 teams, have your competed in?")

    @classmethod
    async def confirm_profile(cls, ui) -> bool:
        """Confirms user profile and returns status."""
        alert_embed: discord.Embed = utils.Alert.create_embed(utils.Alert.Style.WARNING,
            title="Confirm?",
            description="To confirm your profile, react with \u2611\ufe0f. To reenter your profile, react with \u23ea.")
        ui.embed.title, ui.embed.description, ui.embed.color = alert_embed.title, alert_embed.description, alert_embed.color
        reply = await ui.get_valid_reaction(['\u2611\ufe0f', '\u23ea'])
        return reply.emoji == '\u2611\ufe0f'

    @classmethod
    def parse_reply(cls, key, value):
        """Check if reply is valid for the key, return cleaned reply, or false in invalid."""
        if key == "IGN":
            return value if 1 <= len(value) <= 10 else False
        if key == "SW":
            value: str = re.sub(r"[\D]", "", value)
            return value if len(value) == 12 else False
        if key == "Ranks":
            value = value.upper()
            if value in {"C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S"}:  # Standard rank, or default X
                return utils.Profile.convert_rank_power(value)
            if re.search(r"(^S\+\d$)|(^X[1-9]\d{3}(\.\d)?$)", value.upper()):  # S+ or X(power)
                return utils.Profile.convert_rank_power(value)

        return False

    @classmethod
    def create_playstyle_list(cls, profile_playstyles=()) -> str:
        """Create the list of playstyles based on the current profiles."""
        set_checkmark = lambda p: '\u2705' if p in profile_playstyles else '\U0001f7e9'
        return "\n".join([f'{set_checkmark(playstyle)} {playstyle.capitalize()}' for playstyle in utils.Profile.playstyles])
