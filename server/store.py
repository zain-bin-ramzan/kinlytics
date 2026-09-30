from threading import Lock
from uuid import uuid4
from typing import Dict

class RoundStore:
    def __init__(self):
        self._rounds: Dict[str, dict] = {}
        self._lock = Lock()

    def create(self, date: str, expected_clients: int, min_participants: int) -> str:
        rid = str(uuid4())
        with self._lock:
            self._rounds[rid] = {
                "id": rid,
                "date": date,
                "expected_clients": expected_clients,
                "min_participants": min_participants,
                "status": "open",
                "contributions": {}, 
            }
        return rid

    def add(self, rid: str, client_id: str, payload: dict) -> str:
        with self._lock:
            r = self._rounds.get(rid)
            if not r: return "unknown_round"
            if r["status"] != "open": return "round_closed"
            if client_id in r["contributions"]: return "duplicate"
            r["contributions"][client_id] = payload
            return "ok"

    def get(self, rid: str):
        return self._rounds.get(rid)

    def close(self, rid: str) -> bool:
        with self._lock:
            r = self._rounds.get(rid)
            if not r or r["status"] != "open": return False
            r["status"] = "closed"
            return True

    def reset(self):
        with self._lock:
            self._rounds.clear()
            
store = RoundStore()