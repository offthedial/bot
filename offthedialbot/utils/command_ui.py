"""Contains CommandUI class."""

import asyncio
import re
from contextlib import asynccontextmanager
from typing import Union, Callable, Optional, Tuple

import discord
from discord.ext.commands import Context

from offthedialbot import utils


class CommandUI:
    """Custom command UI."""

    def __init__(self, ctx: Context, embed: discord.Embed, **kwargs):
        """Initilize command UI and declare self variables."""
        self.ctx: Context = ctx
        self.embed: discord.Embed = embed
        self.reply_task: Optional[asyncio.Task] = None
        self.alert: Optional[utils.Alert] = None

    async def __new__(cls, ctx: Context, embed: discord.Embed, **kwargs):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)
        self.__init__(ctx, embed, **kwargs)

        await self.check_pemissions(ctx, kwargs)

        self.ui = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def check_pemissions(ctx, required_roles):
        """Check if the user has the correct permissions to execute the command."""
        if required_roles.get("moderator") and not ("moderator" in [role.name.lower() for role in ctx.author.roles]):
            await utils.Alert(
                ctx, utils.Alert.Style.DANGER,
                title="Permission Denied.", description="You don't have permission to use this command."
            )
            raise utils.exc.CommandCancel

    @staticmethod
    async def create_ui(ctx: Context, embed: discord.Embed) -> discord.Message:
        """Create and return the discord embed UI."""
        ui: discord.Message = await ctx.send(embed=embed)
        await ui.add_reaction('❌')
        return ui

    async def update(self) -> None:
        """Update the ui with new information."""
        await self.ui.edit(embed=self.embed)

    async def end(self, status: Union[bool, None]) -> None:
        """End UI interaction and display status."""
        status_key: dict = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED}
        if status_key.get(status):
            await self.ui.edit(embed=status_key[status])
            await self.ui.clear_reactions()
        else:
            await self.ui.delete()
        await self.delete_alert()

        # Raise exception to cancel command
        raise utils.exc.CommandCancel(status, self)

    async def get_valid_message(self, valid: Union[str, Callable], error_fields: dict = None, *, _alert_params=None, **get_reply_params) -> discord.Message:
        """Get message reply with validity checks."""
        # Check if it's the function's first run
        if _alert_params is None:  # Initilize error params
            _alert_params: dict = {**error_fields, "style": utils.Alert.Style.DANGER}
        else:
            await self.update()
            await self.delete_alert()
            await self.create_alert(**_alert_params)

        # Get message and check if it's valid
        reply: discord.Message = await self.get_reply(**get_reply_params)
        if self.check_valid(valid, reply.content):
            await self.delete_alert()
        else:
            reply: discord.Message = await self.get_valid_message(valid=valid, _alert_params=_alert_params)

        return reply

    async def get_reply(self, event: str = 'message', *, valid_reactions: list = None, **kwargs) -> discord.Message:
        """Get the reply from the user."""
        await self.update()  # First update embed

        # Add valid reactions if valids are specified
        for react in (valid_reactions if valid_reactions else []):
            await self.ui.add_reaction(react)

        # Key that determines which check to use for the event
        key = {
            'message': {
                "check": lambda m: utils.checks.msg(m, self.ctx),
                "delete": lambda r: r.delete()
            },
            'reaction_add': {
                "check": lambda r, u: utils.checks.react((r, u), self.ctx, self.ui, valids=valid_reactions),
                "delete": lambda r: self.ui.remove_reaction(r[0].emoji, r[1])
            }
        }
        # Create tasks
        reply_task: asyncio.Task = asyncio.create_task(self.ctx.bot.wait_for(event, check=key[event]["check"]))
        cancel_task: asyncio.Task = self.create_cancel_task(kwargs.get("timeout"))

        # Await tasks
        if kwargs.get("cancel") is False:
            task, reply = reply_task, await reply_task
        else:
            task, reply = await self.wait_tasks({reply_task, cancel_task})

        # Get result
        if task == cancel_task:
            await self.end(status=False)
        else:
            await key[event]["delete"](reply)
            if event.startswith('reaction'):
                reply = reply[0]

            # Remove valid reactions if valids are specified
            if len(valid_reactions := valid_reactions if valid_reactions else []) < 3:
                for react in valid_reactions:
                    await self.ui.remove_reaction(react, self.ctx.me)
            else:
                await self.ui.clear_reactions()
                await self.ui.add_reaction('❌')

        return reply

    async def create_alert(self, style: utils.Alert.Style, title: str, description: str) -> None:
        """Create an alert with a given color to determine the style."""
        self.alert = await utils.Alert(self.ctx, style, title=title, description=description)

    async def delete_alert(self) -> None:
        """Delete an alert associated with the command ui if it exists."""
        if self.alert:
            await self.alert.delete()
            self.alert = None

    async def run_command(self, main):
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
                await main(self.ctx)
        except utils.exc.CommandCancel as e:
            if e.ui:
                await e.ui.ui.delete()
            if e.status == False:
                await self.end(e.status)
            return e

    @staticmethod
    def check_valid(valid: Union[str, Callable], reply: discord.Message) -> bool:
        """Check if a user's reply is valid."""
        if isinstance(valid, str):
            return bool(re.search(valid, reply))
        else:
            try:
                return valid(reply)
            except ValueError:
                return False

    @staticmethod
    async def wait_tasks(tasks: set) -> Tuple[asyncio.Future, Optional[discord.Message]]:
        """Try block to asyncio.wait a set of tasks with timeout handling, and return the first completed."""
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        task: asyncio.Future = done.pop()

        # Get reply
        try:
            reply: Optional[discord.Message] = task.result()
        except asyncio.TimeoutError:
            reply: Optional[discord.Message] = None

        # Cancel the other still pending tasks
        for rest in pending:
            rest.cancel()

        return task, reply

    def create_cancel_task(self, timeout=None) -> asyncio.Task:
        """Create a task that checks if the user canceled the command."""
        return asyncio.create_task(
            self.ctx.bot.wait_for(
                'reaction_add',
                check=lambda r, u: utils.checks.react((r, u), self.ctx, self.ui, valids='❌'),
                timeout=(timeout if timeout else 120)
            )
        )
