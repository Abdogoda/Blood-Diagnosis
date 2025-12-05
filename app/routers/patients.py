# Patients router
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/patients", tags=["patients"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def patient_dashboard(request: Request, db: Session = Depends(get_db)):
    stats = {
        "total_tests": 12,
        "pending_results": 2,
        "last_test_date": "2025-12-01"
    }
    recent_tests = [
        {"date": "2025-12-01", "test_type": "CBC Analysis", "status": "Completed", "result": "Normal"},
        {"date": "2025-11-15", "test_type": "Blood Smear", "status": "Completed", "result": "Normal"},
    ]
    return templates.TemplateResponse("patient/dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_tests": recent_tests
    })

@router.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse("patient/upload_file.html", {"request": request})

@router.get("/result/{test_id}")
async def result_page(request: Request, test_id: int, db: Session = Depends(get_db)):
    result = {
        "test_type": "CBC Analysis",
        "date": "2025-12-01",
        "status": "Completed",
        "diagnosis": "Normal Blood Count",
        "conditions": [
            {"name": "Red Blood Cells", "value": "4.5 M/μL", "status": "Normal", "severity": "low"},
            {"name": "White Blood Cells", "value": "7.2 K/μL", "status": "Normal", "severity": "low"},
        ],
        "recommendations": [
            "Maintain a balanced diet rich in iron",
            "Stay hydrated",
            "Regular exercise recommended"
        ]
    }
    return templates.TemplateResponse("patient/file_result.html", {"request": request, "result": result})

@router.get("/account")
async def account_page(request: Request):
    patient = {
        "name": "Sarah Miller",
        "email": "sarah@example.com",
        "age": 32,
        "phone": "+1 234-567-8900",
        "blood_type": "A+"
    }
    return templates.TemplateResponse("patient/account.html", {"request": request, "patient": patient})
