import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

LOG_DIR = Path("./logs")
LOG_FILE = LOG_DIR / "conversations.jsonl"

_lock = Lock()


def log_turn(session_id: str, user_message: str, bot_response: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user": user_message,
        "bot": bot_response,
    }
    with _lock:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
