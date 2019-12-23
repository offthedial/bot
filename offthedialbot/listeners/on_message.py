async def on_message(self, message):
    await self.process_commands(message)