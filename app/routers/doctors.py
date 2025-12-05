# Doctors router
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/dashboard")
async def doctor_dashboard(db: Session = Depends(get_db)):
    # TODO: Implement doctor dashboard logic
    return {"message": "Doctor dashboard"}

@router.get("/patients")
async def get_patients(db: Session = Depends(get_db)):
    # TODO: Implement get patients logic
    return {"message": "Get patients list"}

@router.get("/reports/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    # TODO: Implement get report logic
    return {"message": f"Get report {report_id}"}
