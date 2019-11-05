"""Holds api for working with a custom command ui."""

import asyncio
import re

import utils


class CommandUI:
    """Class containing the command UI used in each command."""

    def __init__(self, ctx, embed):
        """Initilize command UI and declare self variables."""
        self.ctx = ctx
        self.embed = embed
        self.reply_task = None
        self.error = None

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

    async def end(self, status):
        """End UI interaction and display status."""
        key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED, None: None}
        await self.ctx.ui.edit(embed=key[status])
        await self.ctx.ui.clear_reactions()
        await self.delete_error()

        # Raise exception to cancel command
        raise utils.exc.CommandCancel

    async def get_valid_message(self, valid, error_embed=None, *, _error_params=None):
        """Get message reply with validity checks."""
        # Check if it's the function's first run
        if _error_params is None:  # Initilize error params
            _error_params = {"embed": error_embed, "new": False}
        else:
            await self.update()

        await self.delete_error(**_error_params)

        # Get message and check if it's valid
        reply = await self.get_reply('message')
        if self.check_valid(valid, reply.content):
            _error_params["new"] = False
            await self.delete_error(**_error_params)
        else:
            _error_params["new"] = True
            reply = await self.get_valid_message(valid=valid, _error_params=_error_params)

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
        if wait_result[1] in (cancel_task, None):
            await self.end(status=False)
            reply = False

        else:
            reply = wait_result[0]

            # Delete reply
            await key[event]["delete"](reply)

            # Remove valid reactions if valids are specified
            for react in (valid_reactions if valid_reactions else []):
                await self.ctx.ui.remove_reaction(react, self.ctx.me)

        return reply

    async def delete_error(self, embed=None, new=False):
        """Delete the error and create a new one if specified."""
        if self.error:  # Delete the error, if it exists
            await self.error.delete()
            self.error = None
        if new: self.error = await self.ctx.send(embed=embed)

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

        # Attempt to get result
        try:
            task = done.pop()
            reply = task.result()

        # If timeout occurred
        except asyncio.TimeoutError:
            task = None
            reply = None

        finally:
            # Cancel pending tasks
            for rest in pending:
                rest.cancel()

        return {"reply": reply, "task": task}
