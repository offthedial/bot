from discord.ext import commands as ext
from offthedialbot.commands import register_commands


class Client(ext.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print(f'Logged in as `{self.user.name}`')

    async def on_message(self, message):
        await self.process_commands(message)


client = Client(command_prefix='$')
register_commands(client)
