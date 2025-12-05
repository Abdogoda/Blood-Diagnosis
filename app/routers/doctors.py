# Doctors router
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/doctors", tags=["doctors"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def doctor_dashboard(request: Request, db: Session = Depends(get_db)):
    stats = {
        "total_patients": 45,
        "pending_reports": 12,
        "urgent_cases": 3,
        "completed_today": 8
    }
    recent_patients = [
        {"initials": "SM", "name": "Sarah Miller", "age": 32, "last_visit": "2025-12-05", "status": "Normal"},
        {"initials": "MJ", "name": "Michael Johnson", "age": 45, "last_visit": "2025-12-04", "status": "Review"},
    ]
    return templates.TemplateResponse("doctor/dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_patients": recent_patients
    })

@router.get("/add-patient")
async def add_patient_page(request: Request):
    return templates.TemplateResponse("doctor/add_patient.html", {"request": request})

@router.get("/patient/{patient_id}")
async def patient_profile(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = {
        "name": "Sarah Miller",
        "age": 32,
        "gender": "Female",
        "blood_type": "A+",
        "phone": "+1 234-567-8900",
        "email": "sarah@example.com"
    }
    medical_records = [
        {"date": "2025-12-01", "test": "CBC Analysis", "result": "Normal", "doctor": "Dr. John Doe"},
        {"date": "2025-11-15", "test": "Blood Smear", "result": "Normal", "doctor": "Dr. John Doe"},
    ]
    return templates.TemplateResponse("doctor/patient_profile.html", {
        "request": request,
        "patient": patient,
        "medical_records": medical_records
    })

@router.get("/reports")
async def reports_page(request: Request, db: Session = Depends(get_db)):
    reports = [
        {"id": 1, "patient": "Sarah Miller", "test_type": "CBC Analysis", "date": "2025-12-01", "status": "Completed"},
        {"id": 2, "patient": "Michael Johnson", "test_type": "Blood Smear", "date": "2025-11-28", "status": "Pending"},
    ]
    return templates.TemplateResponse("doctor/reports.html", {"request": request, "reports": reports})

@router.get("/account")
async def account_page(request: Request):
    doctor = {
        "name": "Dr. John Doe",
        "email": "john@example.com",
        "specialization": "Hematology",
        "license": "MD12345",
        "phone": "+1 234-567-8900"
    }
    return templates.TemplateResponse("doctor/account.html", {"request": request, "doctor": doctor})
