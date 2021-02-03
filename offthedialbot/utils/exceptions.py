"""Contains custom exceptions."""


class CommandCancel(Exception):
    """Cancel a command."""

    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description
