"""Holds api for working with a custom command ui."""

import asyncio
import re

from discord import Embed

import utils


class CommandUI:
    """Class containing the command UI used in each command."""

    def __init__(self, ctx, embed):
        """Initilize command UI and declare self variables."""
        self.ctx = ctx
        self.embed = embed
        self.reply_task = None
        self.alert = None

    async def __new__(cls, ctx, embed):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)
        self.__init__(ctx, embed)

        ctx.ui = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def create_ui(ctx, embed):
        """Create and return the discord embed UI."""
        ui = await ctx.send(embed=embed)
        await ui.add_reaction('❌')
        return ui

    async def update(self):
        """Update the ui with new information."""
        await self.ctx.ui.edit(embed=self.embed)

    async def end(self, status, keep_alert=False):
        """End UI interaction and display status."""
        status_key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED, None: None}
        await self.ctx.ui.edit(embed=status_key[status])
        await self.ctx.ui.clear_reactions()
        await self.create_alert(create_new=False, replace=not keep_alert)

        # Raise exception to cancel command
        raise utils.exc.CommandCancel

    async def get_valid_message(self, valid, error_fields: dict = None, *, _alert_params=None):
        """Get message reply with validity checks."""
        # Check if it's the function's first run
        if _alert_params is None:  # Initilize error params
            _alert_params = {**error_fields, "create_new": False}
        else:
            await self.update()

        await self.create_alert(utils.AlertStyle.DANGER, **_alert_params)

        # Get message and check if it's valid
        reply = await self.get_reply('message')
        if self.check_valid(valid, reply.content):
            _alert_params["create_new"] = False
            await self.create_alert(utils.AlertStyle.DANGER, **_alert_params)
        else:
            _alert_params["create_new"] = True
            reply = await self.get_valid_message(valid=valid, _alert_params=_alert_params)

        return reply

    async def get_reply(self, event: str = 'message', *, valid_reactions: list = None):
        """Get the reply from the user."""
        await self.update()  # First update embed

        # Add valid reactions if valids are specified
        for react in (valid_reactions if valid_reactions else []):
            await self.ctx.ui.add_reaction(react)

        # Key that determines which check to use for the event
        key = {
            'message': {
                "check": lambda m: utils.checks.msg(m, self.ctx),
                "delete": lambda r: r.delete()
            },
            'reaction_add': {
                "check": lambda r, u: utils.checks.react((r, u), self.ctx, valids=valid_reactions),
                "delete": lambda r: self.ctx.ui.remove_reaction(r[0].emoji, r[1])
            }
        }
        # Create Tasks
        reply_task = asyncio.create_task(self.ctx.bot.wait_for(event, check=key[event]["check"]))
        cancel_task = asyncio.create_task(
            self.ctx.bot.wait_for(
                'reaction_add', check=lambda r, u: utils.checks.react((r, u), self.ctx, valids='❌'), timeout=120
            )
        )
        # asyncio.wait the set of tasks
        wait_result = await self.wait_tasks({reply_task, cancel_task})

        # Get result
        if wait_result["task"] != reply_task:
            await self.end(status=False)
        else:
            await key[event]["delete"](wait_result["reply"])

            # Remove valid reactions if valids are specified
            for react in (valid_reactions if valid_reactions else []):
                await self.ctx.ui.remove_reaction(react, self.ctx.me)

        return wait_result["reply"]

    async def create_alert(
        self, color: utils.AlertStyle = None, title: str = None, description: str = None, replace=True, create_new=True
    ):
        """Create an alert with a given color to determine the style."""
        if replace:
            await self.delete_alert()

        if create_new:
            title_key = {
                utils.AlertStyle.DANGER: lambda t: f'\U0001f6ab Error: **{t}**',
                utils.AlertStyle.WARNING: lambda t: f'\u26a0 Warning: **{t}**',
                utils.AlertStyle.INFO: lambda t: f'\u2139 Info: **{t}**',
                utils.AlertStyle.SUCCESS: lambda t: f'\u2705 Success: **{t}**',
            }
            embed = Embed(title=title_key[color](title), description=description, color=color)
            self.alert = await self.ctx.send(embed=embed)

    async def delete_alert(self):
        """Delete an alert, ensures message is removed once deleted, and that message exists."""
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

        return {"reply": reply, "task": task}
