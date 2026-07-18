import os
import subprocess


class SystemManager:

    def clear_console(self) -> None:
        """Clear the current terminal window."""
        command = "cls" if os.name == "nt" else "clear"

        subprocess.run(
            command,
            shell=True,
            check=False,
        )