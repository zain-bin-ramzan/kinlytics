from models import RoundCreate, Contribution, RoundStatus, RoundResult
from services.round_service import service

class RoundController:
    def create(self, body: RoundCreate) -> RoundStatus:
        r = service.create_round(body.date, body.min_participants)
        return self._to_status(r)
    
    def result(self, round_id: str) -> RoundResult:
        return RoundResult(**service.compute_result(round_id))
    
    def submit(self, round_id: str, body: Contribution) -> dict:
        service.submit_contribution(
            round_id, body.client_id, body.date, body.model_dump()
        )
        return {"status": "accepted"}

    def get(self, round_id: str) -> RoundStatus:
        return self._to_status(service.get_round(round_id))

    def close(self, round_id: str) -> dict:
        service.close_round(round_id)
        return {"status": "closed"}

    @staticmethod
    def _to_status(r: dict) -> RoundStatus:
        return RoundStatus(
            round_id=r["id"],
            date=r["date"],
            expected_clients=r["expected_clients"],
            received=len(r["contributions"]),
            valid_clients=list(r["contributions"].keys()),
            status=r["status"],
        )

controller = RoundController()