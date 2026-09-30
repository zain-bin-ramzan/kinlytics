from store import store
from collections import defaultdict

class DomainError(Exception):
    def __init__(self, code: str, http: int = 400):
        self.code = code
        self.http = http
        super().__init__(code)

class RoundService:
    def create_round(self, date: str, min_participants: int) -> dict:
        rid = store.create(date, expected_clients=0, min_participants=min_participants)
        return store.get(rid)

    def get_round(self, round_id: str) -> dict:
        r = store.get(round_id)
        if not r:
            raise DomainError("unknown_round", 404)
        return r

    def submit_contribution(self, round_id: str, client_id: str, date: str, payload: dict) -> None:
        r = self.get_round(round_id)
        if payload.get("date") != r["date"]:
            raise DomainError("date_mismatch", 400)
        result = store.add(round_id, client_id, payload)
        if result != "ok":
            raise DomainError(result, 409)

    def close_round(self, round_id: str) -> None:
        self.get_round(round_id)
        if not store.close(round_id):
            raise DomainError("cannot_close", 409)



    def compute_result(self, round_id: str) -> dict:
        r = self.get_round(round_id)
        contributions = list(r["contributions"].values())
        n = len(contributions)

        if n < r["min_participants"]:
            return {
                "round_id": r["id"],
                "date": r["date"],
                "status": r["status"],
                "participants_used": n,
                "average_screen_time_minutes": None,
                "app_ranking": None,
                "released": False,
                "reason": f"only {n} of {r['min_participants']} required participants",
            }

        avg = sum(c["total_screen_time_minutes"] for c in contributions) / n

        app_totals: dict[str, float] = defaultdict(float)
        for c in contributions:
            for app_id, mins in c.get("app_usage_minutes", {}).items():
                app_totals[app_id] += mins

        ranking = [
            {"app_id": a, "total_minutes": round(m, 2)}
            for a, m in sorted(app_totals.items(), key=lambda kv: (-kv[1], kv[0]))
        ]

        return {
            "round_id": r["id"],
            "date": r["date"],
            "status": r["status"],
            "participants_used": n,
            "average_screen_time_minutes": round(avg, 2),
            "app_ranking": ranking,
            "released": True,
            "reason": None,
        }
service = RoundService()