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

        self.ui = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def create_ui(ctx: Context, embed: discord.Embed) -> discord.Message:
        """Create and return the discord embed UI."""
        ui: discord.Message = await ctx.send(embed=embed)
        await ui.add_reaction('❌')
        return ui

    async def get_valid_message(self, valid: Union[str, Callable], error_fields: dict = None, *,
                                _alert_params=None, **get_reply_params) -> discord.Message:
        """Get message reply with validity checks."""
        await self.update()
        # Check if it's the function's first run
        if _alert_params is None:  # Initialize error params
            first = True
            _alert_params: dict = {
                "title": "Invalid Message",
                **(error_fields if error_fields else {}),
                "style": utils.Alert.Style.DANGER
            }
        else:
            first = False
            await self.delete_alert()
            await self.create_alert(**_alert_params)

        # Get message
        reply: discord.Message = await self.get_reply(**get_reply_params)

        # Make sure it's valid
        if self.check_valid(valid, reply):
            if not first:  await self.delete_alert()
        else:
            reply: discord.Message = await self.get_valid_message(
                valid=valid, _alert_params=_alert_params, **get_reply_params
            )
        return reply

    async def get_valid_reaction(self, valid: list, error_fields: dict = None, *,
                                 _alert_params=None, **get_reply_params) -> discord.Reaction:
        """Get reaction reply with validity checks."""
        await self.update()
        # Check if it's the function's first run
        if _alert_params is None:  # Initialize error params
            first = True
            _alert_params: dict = {
                "title": "Invalid Option",
                "description": "Please choose one of the supported options",
                **(error_fields if error_fields else {}),
                "style": utils.Alert.Style.DANGER
            }
            for react in valid:  # Add reactions
                await self.ui.add_reaction(react)
        else:
            first = False
            await self.delete_alert()
            await self.create_alert(**_alert_params)

        # Get reaction
        reply: discord.Reaction = await self.get_reply("reaction_add", **get_reply_params)

        # Make sure it's valid
        if self.check_valid(valid, reply):
            if not first:  await self.delete_alert()
            # Remove reactions
            if len(valid) < 3:
                for react in valid:
                    await self.ui.remove_reaction(react, self.ctx.me)
            else:
                await self.ui.clear_reactions()
                await self.ui.add_reaction('❌')
        else:
            reply: discord.Reaction = await self.get_valid_reaction(
                valid=valid, _alert_params=_alert_params, **get_reply_params
            )
        return reply

    async def get_reply(self, event: str = 'message', /, **kwargs) -> Union[discord.Message, discord.Reaction]:
        """Get the reply from the user."""
        await self.update()

        # Key that determines which check to use for the event
        key = {
            'message': {
                "check": utils.checks.msg(self.ctx),
                "delete": lambda m: m.delete()
            },
            'reaction_add': {
                "check": utils.checks.react(self.ctx, self.ui),
                "delete": lambda r: self.ui.remove_reaction(r[0].emoji, r[1])
            }
        }
        # Create tasks
        reply_task: asyncio.Task = asyncio.create_task(
            self.ctx.bot.wait_for(event, check=key[event]["check"]), name="CommandUI.reply_task")
        cancel_task: Optional[asyncio.Task] = None

        # Await tasks
        if kwargs.get("cancel") is False:
            task, reply = await self.wait_tasks({reply_task})
        else:
            cancel_task = self.create_cancel_task(kwargs.get("timeout"))
            task, reply = await self.wait_tasks({reply_task, cancel_task})

        # Get result
        if task == cancel_task:
            await self.end(status=False)
        else:
            await key[event]["delete"](reply)
            if event.startswith('reaction'):
                reply = reply[0]

        return reply

    async def update(self) -> None:
        """Update the ui with new information."""
        await self.ui.edit(embed=self.embed)

    async def end(self, status: Union[bool, None]) -> None:
        """End UI interaction and display status."""
        status_key: dict = {
            True: discord.Embed(title="Success!", color=utils.Alert.Style.SUCCESS),
            False: discord.Embed(title="Canceled.", color=utils.Alert.Style.DANGER),
        }
        if status_key.get(status):
            await self.ui.edit(embed=status_key[status])
            await self.ui.clear_reactions()
        else:
            await self.ui.delete()
        await self.delete_alerts()

        # Raise exception to cancel command
        raise utils.exc.CommandCancel(status, self)

    async def create_alert(self, *args, **kwargs) -> None:
        """Create an alert associated with the command ui."""
        self.alerts.append(await utils.Alert(self.ctx, *args, **kwargs))

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

        @asynccontextmanager
        async def hide_x():
            try:
                await self.ui.remove_reaction('❌', self.ctx.me)
                yield
            finally:
                await self.ui.add_reaction('❌')

        try:
            async with hide_x():
                await main(self.ctx, *args)
        except utils.exc.CommandCancel as e:
            if e.ui and e.status is not None:
                await e.ui.ui.delete()
            if not e.status:
                await self.end(e.status)
            return e

    def create_cancel_task(self, timeout=None) -> asyncio.Task:
        """Create a task that checks if the user canceled the command."""
        return asyncio.create_task(
            self.ctx.bot.wait_for('reaction_add',
                check=utils.checks.react(self.ctx, self.ui, valids='❌'),
                timeout=(timeout if timeout else 180)), name="CommandUI.cancel_task")

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

    @classmethod
    async def wait_tasks(cls, tasks: Set[asyncio.Task]) -> Tuple[asyncio.Future, Any]:
        """Try block to asyncio.wait a set of tasks with timeout handling, and return the first completed."""
        # Shortcut for 1-task sets
        if len(tasks) == 1:
            task = tasks.pop()
            return task, await cls.wait_task(task)

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        task: asyncio.Future = done.pop()

        # Get reply
        try:
            reply = task.result()
        except asyncio.TimeoutError:
            reply = None
        finally:
            # Cancel the other still pending tasks
            for rest in pending:
                rest.cancel()

        return task, reply

    @staticmethod
    async def wait_task(task: Union[asyncio.Task, asyncio.Future]):
        """Try block to wait a singular task with timeout handling."""
        try:
            return await task
        except asyncio.TimeoutError:
            return None
