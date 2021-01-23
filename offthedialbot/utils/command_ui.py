"""Contains the CommandUI class."""

import asyncio
import re
from contextlib import asynccontextmanager
from typing import List, Tuple, Set, Callable, Optional, Union, Any

import discord
from discord.ext.commands import Context

from offthedialbot import utils


class CommandUI:
    """Custom command UI."""

    def __init__(self, ctx: Context, embed: discord.Embed):
        """Initilize command UI and declare self variables."""
        self.ctx: Context = ctx
        self.embed: discord.Embed = embed
        self.reply_task: Optional[asyncio.Task] = None
        self.alerts: List[utils.Alert] = []

    async def __new__(cls, ctx: Context, embed: discord.Embed):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)
        self.__init__(ctx, embed)

        self.message = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def create_ui(ctx: Context, embed: discord.Embed) -> discord.Message:
        """Create and return the discord embed UI."""
        if embed.colour == discord.Embed.Empty:
            embed.colour = utils.colors.DIALER
        if embed.footer.text == discord.Embed.Empty:
            embed.set_footer(text=f"Invoked: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        message: discord.Message = await ctx.send(embed=embed)
        return message

    async def get_valid(self, event, /, *args, **kwargs):
        """Get a reply with validity checks."""
        coro = {
            "message": lambda: self.get_valid_message(*args, **kwargs),
            "reaction_add": lambda: self.get_valid_reaction(*args, **kwargs)
        }[event]
        return await coro()

    async def get_valid_message(self, valid: Union[str, Callable], error_fields: dict = None, *,
                                _alert_params=None, _alert_index=None, **get_reply_params) -> discord.Message:
        """Get message reply with validity checks."""
        await self.update()
        # Check if it's the function's first run
        if _alert_params is None:  # Initialize error params
            _alert_params: dict = {
                "title": "Invalid Message",
                **(error_fields if error_fields else {}),
                "style": utils.Alert.Style.DANGER
            }
        else:
            _alert_index = await self.create_alert(**_alert_params)

        # Get message
        reply: discord.Message = await self.get_reply(**get_reply_params)
        if isinstance(_alert_index, int):
            await self.delete_alert(_alert_index)

        # Make sure it's valid
        if not self.check_valid(valid, reply):
            reply: discord.Message = await self.get_valid_message(
                valid=valid, _alert_params=_alert_params, _alert_index=_alert_index, **get_reply_params
            )
        return reply

    async def get_valid_reaction(self, valid: list, error_fields: dict = None, *,
                                 _alert_params=None, _alert_index=None, **get_reply_params) -> discord.Reaction:
        """Get reaction reply with validity checks."""
        await self.update()
        # Check if it's the function's first run
        if _alert_params is None:  # Initialize error params
            _alert_params: dict = {
                "title": "Invalid Option",
                "description": "Please choose one of the supported options",
                **(error_fields if error_fields else {}),
                "style": utils.Alert.Style.DANGER
            }
            if get_reply_params.get("cancel", True) is True:
                await self.message.add_reaction('❌')
            for react in valid:  # Add reactions
                await self.message.add_reaction(react)
        else:
            _alert_index = await self.create_alert(**_alert_params)

        # Get reaction
        reply: discord.Reaction = await self.get_reply("reaction_add", **get_reply_params)
        if isinstance(_alert_index, int):
            await self.delete_alert(_alert_index)

        # Make sure it's valid
        if not self.check_valid(valid, reply):
            reply: discord.Reaction = await self.get_valid_reaction(
                valid=valid, _alert_params=_alert_params, _alert_index=_alert_index, **get_reply_params
            )
        await self.remove_reactions(valid, self.message)
        return reply

    async def get_reply(self, event: str = 'message', /, **kwargs) -> Union[discord.Message, discord.Reaction]:
        """Get the reply from the user."""
        await self.update()

        # Key that determines which check to use for the event
        key = {
            'message': {
                "check": utils.checks.msg(self.ctx.author, self.ctx.channel),
                "delete": lambda m: m.delete()
            },
            'reaction_add': {
                "check": utils.checks.react(self.ctx.author, self.message),
                "delete": lambda r: self.message.clear_reaction(r[0].emoji)
            }
        }
        # Create tasks
        reply_task = asyncio.create_task(self.ctx.bot.wait_for(event, check=key[event]["check"]), name="CommandUI.reply_task")
        cancel_task = await self.create_cancel_task(kwargs.get("cancel", True))

        # Await tasks
        tasks = {reply_task, cancel_task} if cancel_task else {reply_task}
        task, reply = await self.wait_tasks(tasks, kwargs.get("timeout", 180))

        # Get result
        if task is reply_task:
            if kwargs.get("delete") is not False:
                await key[event]["delete"](reply)
            if event.startswith('reaction'):
                reply = reply[0]
        else:
            print(task)
            await self.end(False, None if task else "Command Timeout")

        return reply

    async def create_alert(self, *args, **kwargs) -> int:
        """Create an alert associated with the command ui."""
        self.alerts.append(alert := await utils.Alert(self.ctx, *args, **kwargs))
        return self.alerts.index(alert)

    @asynccontextmanager
    async def create_temp_alert(self, *args, **kwargs) -> int:
        """Create an alert associated with the command ui."""
        alert = None
        try:
            alert = await self.create_alert(*args, **kwargs)
            yield alert
        finally:
            if alert is not None:
                await self.delete_alert(alert)

    async def delete_alert(self, index=-1) -> None:
        """Delete an alert associated with the command ui if it exists, defaults the the latest alert."""
        if self.alerts:
            await self.alerts[index].delete()

    async def delete_alerts(self) -> None:
        """Delete all alerts associated with the command ui if it exists."""
        for alert in self.alerts:
            await alert.delete()

    async def run_command(self, main, *args):
        """Run an external command, from a command ui."""
        await self.message.clear_reaction('❌')
        try:
            await main(self.ctx, *args)
        except utils.exc.CommandCancel as e:
            if e.ui and e.status is not None:
                await e.ui.message.delete()
            if not e.status:
                await self.end(e.status, e.title, e.description)
            return e

    async def end(self, status: Union[bool, None], title: str = None, description=discord.Embed.Empty) -> None:
        """End UI interaction and display status."""
        status_key: dict = {
            True: utils.Alert.create_embed(utils.Alert.Style.SUCCESS,
                title=title if title else "Command Complete", description=description),
            False: utils.Alert.create_embed(utils.Alert.Style.DANGER,
                title=title if title else "Command Canceled", description=description),
        }
        # Get embed
        if isinstance(status, discord.Embed):
            embed = status
        elif status_key.get(status):
            embed = status_key[status]
        else:
            embed = None

        # Update message
        if embed:
            await self.message.edit(embed=embed)
            await self.message.clear_reactions()
        else:
            await self.message.delete()
        await self.delete_alerts()

        # Raise exception to cancel command
        raise utils.exc.CommandCancel(status, ui=self, title=title, description=description)

    async def create_cancel_task(self, value=True) -> asyncio.Task:
        """Create a task that checks if the user canceled the command."""
        if value is True:
            await self.message.add_reaction('❌')
            return self.cancel_task()
        if value is False:
            await self.message.clear_reaction('❌')

    def cancel_task(self):
        """Task that checks if the user canceled the command."""
        return asyncio.create_task(
            self.ctx.bot.wait_for('reaction_add',
                check=utils.checks.react(self.ctx.author, self.message, valids={'❌'})),
            name="CommandUI.cancel_task")

    async def update(self) -> None:
        """Update the ui with new information."""
        await self.message.edit(embed=self.embed)

    @classmethod
    async def wait_tasks(cls, tasks: Set[asyncio.Task], timeout=None) -> Tuple[Optional[asyncio.Future], Optional[Any]]:
        """
        Try block to asyncio.wait a set of tasks with timeout handling.

        :return: A tuple containing the task and the result. Both will be None if a timeout occurs.
        """
        done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        for rest in pending:
            rest.cancel()

        if done:
            task: asyncio.Future = done.pop()
            return task, task.result()

        return None, None

    @staticmethod
    def check_valid(valid, reply: Union[discord.Message, discord.Reaction]) -> bool:
        """Check if a user's reply is valid."""
        if isinstance(valid, str):
            return bool(re.search(valid, reply.content))
        if getattr(valid, "__contains__", False):
            return reply.emoji in valid

        else:
            try:
                return valid(reply)
            except ValueError:
                return False

    @staticmethod
    async def remove_reactions(reactions, message):
        """Efficiently remove reactions."""
        if len(reactions) < 3:
            for react in reactions:
                await message.clear_reaction(react)
        else:
            await message.clear_reactions()
