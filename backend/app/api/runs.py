from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.run import RunCreate, RunResponse, RunDetailResponse, RunInstructionCreate
from backend.app.schemas.event import EventCreate, EventResponse
from backend.app.services import run_service, event_service

router = APIRouter(prefix="/api/runs", tags=["runs"])

@router.post("", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
def create_run(
    run_in: RunCreate,
    db: Session = Depends(get_db)
):
    try:
        return run_service.create_run(db, run_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[RunResponse])
def get_runs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return run_service.get_runs(db, skip=skip, limit=limit)

@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    run = run_service.get_run(db, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found"
        )
    return run

@router.post("/{run_id}/events", response_model=EventResponse, status_code=status.HTTP_200_OK)
def send_event_to_run(
    run_id: int,
    event_in: EventCreate,
    db: Session = Depends(get_db)
):
    try:
        return event_service.send_event_to_run(db, run_id, event_in)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

@router.post("/{run_id}/instructions", response_model=RunResponse, status_code=status.HTTP_200_OK)
def add_instruction_to_run(
    run_id: int,
    instruction_in: RunInstructionCreate,
    db: Session = Depends(get_db)
):
    try:
        return run_service.add_run_instruction(db, run_id, instruction_in.instruction)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

@router.post("/{run_id}/interrupt", response_model=RunResponse, status_code=status.HTTP_200_OK)
def interrupt_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    try:
        return run_service.interrupt_run(db, run_id)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

@router.post("/{run_id}/resume", response_model=RunResponse, status_code=status.HTTP_200_OK)
def resume_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    try:
        return run_service.resume_run(db, run_id)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

@router.post("/{run_id}/terminate", response_model=RunResponse, status_code=status.HTTP_200_OK)
def terminate_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    try:
        return run_service.terminate_run(db, run_id)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )
