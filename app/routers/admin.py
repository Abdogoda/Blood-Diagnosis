# Admin router for admin-specific routes
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role
from app.services.flash_messages import set_flash_message
import os
import uuid
from pathlib import Path

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


@router.get("/account")
async def account_page(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Get user phones
    phones = current_user.phones
    phone = phones[0].phone if phones else None
    
    return templates.TemplateResponse("admin/account.html", {
        "request": request,
        "current_user": current_user,
        "admin": current_user,
        "phone": phone
    })


@router.post("/update-profile")
async def update_profile(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Check if email already exists for another user
    existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        response = RedirectResponse(url="/admin/account", status_code=303)
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
    
    db.commit()
    db.refresh(current_user)
    
    response = RedirectResponse(url="/admin/account", status_code=303)
    set_flash_message(response, "success", "Profile updated successfully!")
    return response


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    from app.services.password_utils import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(current_password, current_user.password):
        response = RedirectResponse(url="/admin/account", status_code=303)
        set_flash_message(response, "error", "Current password is incorrect")
        return response
    
    # Check if new passwords match
    if new_password != confirm_password:
        response = RedirectResponse(url="/admin/account", status_code=303)
        set_flash_message(response, "error", "New passwords do not match")
        return response
    
    # Check password length
    if len(new_password) < 8:
        response = RedirectResponse(url="/admin/account", status_code=303)
        set_flash_message(response, "error", "Password must be at least 8 characters long")
        return response
    
    # Update password
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    response = RedirectResponse(url="/admin/account", status_code=303)
    set_flash_message(response, "success", "Password changed successfully!")
    return response


@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_ext = os.path.splitext(profile_image.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        response = RedirectResponse(url="/admin/account", status_code=303)
        set_flash_message(response, "error", "Invalid file type. Only JPG, PNG, and GIF are allowed")
        return response
    
    # Create uploads/profiles directory if it doesn't exist
    upload_dir = Path("uploads/profiles")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Delete old profile image if exists
    if current_user.profile_image:
        old_file = Path(current_user.profile_image)
        if old_file.exists():
            old_file.unlink()
    
    # Save new file
    with open(file_path, "wb") as buffer:
        content = await profile_image.read()
        buffer.write(content)
    
    # Update user profile_image path
    current_user.profile_image = str(file_path)
    db.commit()
    
    response = RedirectResponse(url="/admin/account", status_code=303)
    set_flash_message(response, "success", "Profile image updated successfully!")
    return response
