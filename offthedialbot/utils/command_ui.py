"""Holds api for working with a custom command ui."""

from discord import Embed
from discord.ext.commands import context
import asyncio
import re

import utils


class CommandUI:
    """Class containing the command UI used in each command."""

    def __init__(self, ctx: context, embed: Embed):
        """Initilize command UI and declare self variables."""
        self.ctx = ctx
        self.embed = embed
        self.reply_task = None
        self.alert = None

    async def __new__(cls, ctx: context, embed: Embed):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)
        self.__init__(ctx, embed)

        self.ui = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def create_ui(ctx: context, embed: Embed):
        """Create and return the discord embed UI."""
        ui = await ctx.send(embed=embed)
        await ui.add_reaction('❌')
        return ui

    async def update(self):
        """Update the ui with new information."""
        await self.ui.edit(embed=self.embed)

    async def end(self, status: bool):
        """End UI interaction and display status."""
        status_key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED}
        if status_key.get(status):
            await self.ui.edit(embed=status_key[status])
            await self.ui.clear_reactions()
        else:
            await self.ui.delete()
        await self.delete_alert()

        # Raise exception to cancel command
        raise utils.exc.CommandCancel

    async def get_valid_message(self, valid, error_fields: dict = None, *, _alert_params=None):
        """Get message reply with validity checks."""
        # Check if it's the function's first run
        if _alert_params is None:  # Initilize error params
            _alert_params = {**error_fields, "style": utils.Alert.Style.DANGER}
        else:
            await self.update()
            await self.delete_alert()
            await self.create_alert(**_alert_params)

        # Get message and check if it's valid
        reply = await self.get_reply()
        if self.check_valid(valid, reply.content):
            await self.delete_alert()
        else:
            reply = await self.get_valid_message(valid=valid, _alert_params=_alert_params)

        return reply

    async def get_reply(self, event: str = 'message', *, valid_reactions: list = None, cancel=True):
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
        reply_task = asyncio.create_task(self.ctx.bot.wait_for(event, check=key[event]["check"]))
        cancel_task = self.create_cancel_task()

        # Await tasks
        if cancel:
            task, reply = await self.wait_tasks({reply_task, cancel_task})
        else:
            task, reply = reply_task, await reply_task

        # Get result
        if task == cancel_task:
            await self.end(status=False)
        else:
            await key[event]["delete"](reply)

            # Remove valid reactions if valids are specified
            for react in (valid_reactions if valid_reactions else []):
                await self.ui.remove_reaction(react, self.ctx.me)

        return reply

    async def create_alert(self, style: utils.Alert.Style, title: str, description: str):
        """Create an alert with a given color to determine the style."""
        self.alert = await utils.Alert(self.ctx, style, title=title, description=description)

    async def delete_alert(self):
        """Delete an alert associated with the command ui if it exists."""
        if self.alert:
            await self.alert.delete()
            self.alert = None

    @staticmethod
    def check_valid(valid, reply):
        """Check if a user's reply is valid."""
        if isinstance(valid, str):
            return re.search(valid, reply)
        else:
            try:
                return valid(reply)
            except ValueError:
                return False

    @staticmethod
    async def wait_tasks(tasks: set):
        """Try block to asyncio.wait a set of tasks with timeout handling, and return the first completed."""
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        task = done.pop()

        # Get reply
        try:
            reply = task.result()
        except asyncio.TimeoutError:
            reply = None

        # Cancel the other still pending tasks
        for rest in pending:
            rest.cancel()

        return task, reply

    def create_cancel_task(self):
        """Create a task that checks if the user canceled the command."""
        return asyncio.create_task(
            self.ctx.bot.wait_for(
                'reaction_add',
                check=lambda r, u: utils.checks.react((r, u), self.ctx, self.ui, valids='❌'),
                timeout=120
            )
        )
