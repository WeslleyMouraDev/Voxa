import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any, Optional


class JSONStore:
    """Thread-safe and atomic JSON storage handler."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.lock = threading.RLock()

    def read(self, default: Any = None) -> Any:
        """Reads JSON data safely under lock. Returns `default` on missing or corrupt file."""
        with self.lock:
            if not self.file_path.exists():
                return default
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default

    def write(self, data: Any) -> None:
        """Atomically writes data into the JSON file using a temp file and os.replace."""
        with self.lock:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temp_file = self.file_path.with_name(
                f"{self.file_path.name}.{uuid.uuid4().hex}.tmp"
            )
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(temp_file, self.file_path)
            except Exception:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except OSError:
                        pass
                raise
