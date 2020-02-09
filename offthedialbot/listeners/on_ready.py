"""Contains on_ready listener."""


async def on_ready(self):
    """When the bot is ready."""
    self.logger.info(f'Logged in as: {self.user.name}')
