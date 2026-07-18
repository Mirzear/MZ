from datetime import datetime, timedelta


class SessionManager:

    def __init__(self, history_limit: int = 50) -> None:
        self.started_at = datetime.now()
        self.history_limit = history_limit
        self.command_history: list[str] = []

    def register_command(self, command: str) -> None:
        """Register a command in the current session history."""
        self.command_history.append(command)

        if len(self.command_history) > self.history_limit:
            self.command_history.pop(0)

    def get_history(self) -> list[str]:
        """Return a copy of the session command history."""
        return self.command_history.copy()

    def clear_history(self) -> None:
        """Clear the current session command history."""
        self.command_history.clear()

    def get_uptime(self) -> timedelta:
        """Return how long the current session has been running."""
        return datetime.now() - self.started_at

    def get_formatted_uptime(self) -> str:
        """Return the session uptime in a readable format."""
        total_seconds = int(self.get_uptime().total_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"