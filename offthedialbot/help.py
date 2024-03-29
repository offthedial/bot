"""Contains HelpCommand class."""

import discord
from discord.ext import commands

from offthedialbot import utils


class HelpCommand(commands.DefaultHelpCommand):
    """Set up help command for the bot."""

    async def send_bot_help(self, mapping):
        """Send bot command page."""
        list_commands = [
            command for cog in [
                await self.filter_commands(cog_commands)
                for cog, cog_commands in mapping.items()
                if cog is not None and await self.filter_commands(cog_commands)
            ] for command in cog
        ]
        embed = self.create_embed(
            title="`$help`",
            description="All the commands for Off the Dial Bot!",
            fields=[{
                "name": "Commands:",
                "value": "\n".join([
                    self.short(command)
                    for command in await self.filter_commands(mapping[None]) if command.help])
            }, {
                "name": "Misc Commands:",
                "value": "\n".join([
                    self.short(command)
                    for command in list_commands])
            }]
        )
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        """Send cog command page."""
        embed = self.create_embed(
            title=cog.qualified_name.capitalize(),
            description=cog.description,
            **({"fields": [{
                "name": f"{cog.qualified_name.capitalize()} Commands:",
                "value": "\n".join([
                    self.short(command)
                    for command in cog.get_commands()])
            }]} if cog.get_commands() else {}))

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """Send command group page."""
        embed = self.create_embed(
            title=self.short(group, False),
            description=group.help,
            fields=[{
                "name": f"Subcommands:",
                "value": "\n".join([
                    self.short(command)
                    for command in await self.filter_commands(group.commands)
                ])
            }]
        )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """Send command page."""
        embed = self.create_embed(
            title=self.short(command, False),
            description=command.help,
        )
        await self.get_destination().send(embed=embed)

    async def command_not_found(self, string):
        """Returns message when command is not found."""
        return f"Command {self.short(string, False)} does not exist."

    async def subcommand_not_found(self, command, string):
        """Returns message when subcommand is not found."""
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Command {self.short(command, False)} has no subcommand named `{string}`."
        else:
            return f"Command {self.short(command, False)} has no subcommands."

    async def send_error_message(self, error):
        """Send error message, override to support sending embeds."""
        await self.get_destination().send(
            embed=utils.Alert.create_embed(utils.Alert.Style.DANGER,
                title="Command/Subcommand not found.", description=error))

    def create_embed(self, fields: list = (), **kwargs):
        """Create help embed."""
        embed = discord.Embed(color=utils.Alert.Style.DANGER, **kwargs)
        for field in fields:
            embed.add_field(**field, inline=False)
        embed.set_footer(
            text=f"Type {self.clean_prefix}help command for more info on a command. You can also type {self.clean_prefix}help category for more info on a category.")
        return embed

    def short(self, command, doc=True):
        """List the command as a one-liner."""
        sig = self.get_command_signature(command) if not doc else f'{self.clean_prefix}{command}'
        return f'`{sig[:-1] if sig.endswith(" ") else sig}` {(command.short_doc if doc else "")}'


help_command = HelpCommand()
