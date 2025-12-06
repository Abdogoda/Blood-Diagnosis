# Doctors router
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role

router = APIRouter(prefix="/doctor", tags=["doctors"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def doctor_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    stats = {
        "total_patients": 45,
        "pending_reports": 12,
        "urgent_cases": 3,
        "completed_today": 8
    }
    
    # Get recent patients (users with role='patient')
    recent_patients_query = db.query(User).filter(User.role == "patient").limit(5).all()
    recent_patients = [
        {
            "initials": f"{p.fname[0]}{p.lname[0]}",
            "name": f"{p.fname} {p.lname}",
            "last_visit": p.created_at.strftime("%Y-%m-%d"),
            "status": "Normal",
            "id": p.id
        }
        for p in recent_patients_query
    ]
    
    return templates.TemplateResponse("doctor/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "recent_patients": recent_patients
    })

@router.get("/add-patient")
async def add_patient_page(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"]))
):
    return templates.TemplateResponse("doctor/add_patient.html", {
        "request": request,
        "current_user": current_user
    })

@router.get("/patient/{patient_id}")
async def patient_profile(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get patient user
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        return templates.TemplateResponse("doctor/dashboard.html", {
            "request": request,
            "current_user": current_user,
            "error": "Patient not found"
        }, status_code=404)
    
    # Get patient phones
    phones = patient.phones
    phone = phones[0].phone if phones else None
    
    medical_records = [
        {"date": "2025-12-01", "test": "CBC Analysis", "result": "Normal", "doctor": "Dr. John Doe"},
        {"date": "2025-11-15", "test": "Blood Smear", "result": "Normal", "doctor": "Dr. John Doe"},
    ]
    
    return templates.TemplateResponse("doctor/patient_profile.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "phone": phone,
        "medical_records": medical_records
    })

@router.get("/reports")
async def reports_page(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    reports = [
        {"id": 1, "patient": "Sarah Miller", "test_type": "CBC Analysis", "date": "2025-12-01", "status": "Completed"},
        {"id": 2, "patient": "Michael Johnson", "test_type": "Blood Smear", "date": "2025-11-28", "status": "Pending"},
    ]
    return templates.TemplateResponse("doctor/reports.html", {
        "request": request,
        "current_user": current_user,
        "reports": reports
    })

@router.get("/account")
async def account_page(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get doctor info
    doctor_info = db.query(User).filter(User.id == current_user.id).first().doctor_info
    
    # Get user phones
    phones = current_user.phones
    phone = phones[0].phone if phones else None
    
    return templates.TemplateResponse("doctor/account.html", {
        "request": request,
        "current_user": current_user,
        "doctor": current_user,
        "doctor_info": doctor_info,
        "phone": phone
    })
