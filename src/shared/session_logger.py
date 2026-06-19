import json
from datetime import datetime, timezone
from pathlib import Path


class SessionLogger:
    def __init__(self, session_id):
        self.session_id = session_id
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.turns = []

    def record_turn(self, turn):
        self.turns.append(turn)

    def dump(self, directory="logs/sessions", error=None):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / f"{self.session_id}.json"
        payload = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "dumped_at": datetime.now(timezone.utc).isoformat(),
            "turns": self.turns,
        }
        if error is not None:
            payload["error"] = error
        file_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return file_path
