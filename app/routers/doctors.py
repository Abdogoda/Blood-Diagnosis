# Doctors router
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role
from app.services.flash_messages import set_flash_message

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


@router.post("/update-profile")
async def update_profile(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    specialization: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Check if email already exists for another user
    existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        response = RedirectResponse(url="/doctor/account", status_code=303)
        set_flash_message(response, "error", "Email already exists for another user")
        return response
    
    # Update user information
    current_user.fname = fname
    current_user.lname = lname
    current_user.email = email
    
    # Update or create phone number
    if phone:
        from app.database import UserPhone
        user_phone = db.query(UserPhone).filter(UserPhone.user_id == current_user.id).first()
        if user_phone:
            user_phone.phone = phone
        else:
            new_phone = UserPhone(user_id=current_user.id, phone=phone)
            db.add(new_phone)
    
    # Update doctor info
    if specialization:
        doctor_info = current_user.doctor_info
        if doctor_info:
            doctor_info.specialization = specialization
        else:
            from app.database import DoctorInfo
            new_doctor_info = DoctorInfo(
                user_id=current_user.id,
                license_number="TEMP-" + str(current_user.id),
                specialization=specialization
            )
            db.add(new_doctor_info)
    
    db.commit()
    db.refresh(current_user)
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success", "Profile updated successfully!")
    return response


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.password_utils import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(current_password, current_user.password):
        response = RedirectResponse(url="/doctor/account", status_code=303)
        set_flash_message(response, "error", "Current password is incorrect")
        return response
    
    # Check if new passwords match
    if new_password != confirm_password:
        response = RedirectResponse(url="/doctor/account", status_code=303)
        set_flash_message(response, "error", "New passwords do not match")
        return response
    
    # Check password length
    if len(new_password) < 8:
        response = RedirectResponse(url="/doctor/account", status_code=303)
        set_flash_message(response, "error", "Password must be at least 8 characters long")
        return response
    
    # Update password
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success", "Password changed successfully!")
    return response
