from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.supervisor import SupervisorCreate, SupervisorUpdate, SupervisorResponse
from backend.app.services import supervisor_service

router = APIRouter(prefix="/api/supervisors", tags=["supervisors"])

@router.post("", response_model=SupervisorResponse, status_code=status.HTTP_201_CREATED)
def create_supervisor(
    supervisor_in: SupervisorCreate,
    db: Session = Depends(get_db)
):
    return supervisor_service.create_supervisor(db, supervisor_in)

@router.get("", response_model=List[SupervisorResponse])
def get_supervisors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return supervisor_service.get_supervisors(db, skip=skip, limit=limit)

@router.get("/{supervisor_id}", response_model=SupervisorResponse)
def get_supervisor(
    supervisor_id: int,
    db: Session = Depends(get_db)
):
    supervisor = supervisor_service.get_supervisor(db, supervisor_id)
    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor with ID {supervisor_id} not found"
        )
    return supervisor

@router.put("/{supervisor_id}", response_model=SupervisorResponse)
def update_supervisor(
    supervisor_id: int,
    supervisor_in: SupervisorUpdate,
    db: Session = Depends(get_db)
):
    supervisor = supervisor_service.update_supervisor(db, supervisor_id, supervisor_in)
    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor with ID {supervisor_id} not found"
        )
    return supervisor

@router.delete("/{supervisor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supervisor(
    supervisor_id: int,
    db: Session = Depends(get_db)
):
    success = supervisor_service.delete_supervisor(db, supervisor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor with ID {supervisor_id} not found"
        )
    return None
