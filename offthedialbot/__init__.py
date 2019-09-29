from discord.ext import commands


class Client(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print(f'Logged in as `{self.user.name}`')
        pass

    async def on_message(self, message):
        await self.process_commands(message)


client = Client(command_prefix='$')
