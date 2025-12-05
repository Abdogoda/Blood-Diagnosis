# Patients router
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/dashboard")
async def patient_dashboard(db: Session = Depends(get_db)):
    # TODO: Implement patient dashboard logic
    return {"message": "Patient dashboard"}

@router.get("/reports")
async def get_my_reports(db: Session = Depends(get_db)):
    # TODO: Implement get reports logic
    return {"message": "Get my reports"}

@router.get("/profile")
async def get_profile(db: Session = Depends(get_db)):
    # TODO: Implement get profile logic
    return {"message": "Get profile"}
