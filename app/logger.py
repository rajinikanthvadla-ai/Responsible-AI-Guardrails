"""JSONL logger for safety and governance events."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class SafetyLogger:
    """Write structured safety events to a JSONL file."""

    def __init__(self, log_path: str = "logs/safety_events.jsonl") -> None:
        self.path = Path(log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def log_event(self, prompt: str, model_name: str, decision: Dict[str, Any]) -> None:
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "prompt_sha256": self._hash_prompt(prompt),
            "model": model_name,
            "decision": decision,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
