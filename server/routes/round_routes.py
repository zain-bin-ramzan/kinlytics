from fastapi import APIRouter, HTTPException
from models import RoundCreate, Contribution, RoundStatus, RoundResult
from controllers.round_controller import controller
from services.round_service import DomainError

router = APIRouter(prefix="/rounds", tags=["rounds"])

@router.post("", response_model=RoundStatus)
def create_round(body: RoundCreate):
    return controller.create(body)

@router.post("/{round_id}/contributions")
def submit(round_id: str, body: Contribution):
    try:
        return controller.submit(round_id, body)
    except DomainError as e:
        raise HTTPException(e.http, e.code)

@router.get("/{round_id}", response_model=RoundStatus)
def status(round_id: str):
    try:
        return controller.get(round_id)
    except DomainError as e:
        raise HTTPException(e.http, e.code)

@router.post("/{round_id}/close")
def close(round_id: str):
    try:
        return controller.close(round_id)
    except DomainError as e:
        raise HTTPException(e.http, e.code)

@router.get("/{round_id}/result", response_model=RoundResult)
def result(round_id: str):
    try:
        return controller.result(round_id)
    except DomainError as e:
        raise HTTPException(e.http, e.code)