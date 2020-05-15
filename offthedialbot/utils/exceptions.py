"""Contains custom exceptions."""


class CommandCancel(Exception):
    """Cancel a command."""

    def __init__(self, status=None, ui=None, title=None, description=None):
        self.status = status
        self.ui = ui
        self.title = title
        self.description = description
