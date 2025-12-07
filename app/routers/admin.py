# Admin router for admin-specific routes
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    total_patients = db.query(User).filter(User.role == "patient").count()
    
    stats = {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_tests": 0,  # Will be implemented when tests are added
        "model_accuracy": 99.5,
        "avg_processing_time": 2.3
    }
    
    # Get recent users
    recent_users_query = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    recent_users = [
        {
            "initials": f"{u.fname[0]}{u.lname[0]}",
            "name": f"{u.fname} {u.lname}",
            "role": u.role.capitalize(),
            "date": u.created_at.strftime("%Y-%m-%d")
        }
        for u in recent_users_query
    ]
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "recent_users": recent_users
    })


@router.get("/doctors")
def admin_doctors(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    doctors_query = db.query(User).filter(User.role == "doctor").all()
    doctors = [
        {
            "id": d.id,
            "initials": f"{d.fname[0]}{d.lname[0]}",
            "name": f"Dr. {d.fname} {d.lname}",
            "email": d.email,
            "specialization": d.doctor_info.specialization if d.doctor_info else "N/A",
            "patient_count": 0,  # Will be implemented when patient assignments are added
            "status": "active"
        }
        for d in doctors_query
    ]
    
    return templates.TemplateResponse("admin/doctors.html", {
        "request": request,
        "current_user": current_user,
        "doctors": doctors
    })


@router.get("/patients")
def admin_patients(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    patients_query = db.query(User).filter(User.role == "patient").all()
    patients = [
        {
            "id": p.id,
            "initials": f"{p.fname[0]}{p.lname[0]}",
            "name": f"{p.fname} {p.lname}",
            "email": p.email,
            "blood_type": p.blood_type or "N/A",
            "test_count": 0,  # Will be implemented when tests are added
            "last_visit": p.created_at.strftime("%Y-%m-%d")
        }
        for p in patients_query
    ]
    
    return templates.TemplateResponse("admin/patients.html", {
        "request": request,
        "current_user": current_user,
        "patients": patients
    })


@router.get("/models")
def admin_models(
    request: Request,
    current_user: User = Depends(require_role(["admin"]))
):
    models = [
        {"name": "CBC Analysis Model", "version": "2.1", "accuracy": 99.5, "predictions": 10234, "speed": 2.1, "status": "active", "last_updated": "2025-12-01", "type": "Neural Network"},
        {"name": "Blood Image Classifier", "version": "1.8", "accuracy": 98.7, "predictions": 5000, "speed": 2.5, "status": "active", "last_updated": "2025-11-25", "type": "CNN"},
    ]
    return templates.TemplateResponse("admin/models.html", {
        "request": request,
        "current_user": current_user,
        "models": models
    })
