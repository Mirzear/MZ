from datetime import datetime
from pathlib import Path


class Logger:

    def __init__(self, file_name: str = "mz.log") -> None:
        self.base_path = Path(__file__).resolve().parents[2]
        self.logs_path = self.base_path / "logs"
        self.file_path = self.logs_path / file_name

        self.logs_path.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}"

        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(formatted_message + "\n")

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def warning(self, message: str) -> None:
        self.log("WARNING", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)