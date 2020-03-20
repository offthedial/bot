"""Contains custom exceptions."""


class CommandCancel(Exception):
    """Cancel a command."""

    def __init__(self, status=None, ui=None):
        self.status = status
        self.ui = ui
