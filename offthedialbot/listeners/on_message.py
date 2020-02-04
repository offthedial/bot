"""Contains on_message listener."""


async def on_message(self, message):
    """When a new message is sent."""
    await self.process_commands(message)
