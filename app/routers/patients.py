# Patients router
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role
from app.services.flash_messages import set_flash_message
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/patient", tags=["patients"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def patient_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
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
        "current_user": current_user,
        "stats": stats,
        "recent_tests": recent_tests
    })

@router.get("/upload")
async def upload_page(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"]))
):
    return templates.TemplateResponse("patient/upload_file.html", {
        "request": request,
        "current_user": current_user
    })

@router.get("/result/{test_id}")
async def result_page(
    request: Request,
    test_id: int,
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
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
    return templates.TemplateResponse("patient/file_result.html", {
        "request": request,
        "current_user": current_user,
        "result": result
    })

@router.get("/account")
async def account_page(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    # Get user phones
    phones = db.query(User).filter(User.id == current_user.id).first().phones
    phone = phones[0].phone if phones else None
    
    return templates.TemplateResponse("patient/account.html", {
        "request": request,
        "current_user": current_user,
        "patient": current_user,
        "phone": phone
    })


@router.post("/update-profile")
async def update_profile(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    gender: str = Form(None),
    phone: str = Form(None),
    blood_type: str = Form(None),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.flash_messages import set_flash_message
    from fastapi.responses import RedirectResponse
    
    # Check if email already exists for another user
    existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        response = RedirectResponse(url="/patient/account", status_code=303)
        set_flash_message(response, "error", "Email already exists for another user")
        return response
    
    # Update user information
    current_user.fname = fname
    current_user.lname = lname
    current_user.email = email
    current_user.gender = gender
    current_user.blood_type = blood_type
    
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
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success", "Profile updated successfully!")
    return response


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.flash_messages import set_flash_message
    from app.services.password_utils import verify_password, get_password_hash
    from fastapi.responses import RedirectResponse
    
    # Verify current password
    if not verify_password(current_password, current_user.password):
        response = RedirectResponse(url="/patient/account", status_code=303)
        set_flash_message(response, "error", "Current password is incorrect")
        return response
    
    # Check if new passwords match
    if new_password != confirm_password:
        response = RedirectResponse(url="/patient/account", status_code=303)
        set_flash_message(response, "error", "New passwords do not match")
        return response
    
    # Check password length
    if len(new_password) < 8:
        response = RedirectResponse(url="/patient/account", status_code=303)
        set_flash_message(response, "error", "Password must be at least 8 characters long")
        return response
    
    # Update password
    current_user.password = get_password_hash(new_password)
    db.commit()
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success", "Password changed successfully!")
    return response


@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_ext = os.path.splitext(profile_image.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        response = RedirectResponse(url="/patient/account", status_code=303)
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
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success", "Profile image updated successfully!")
    return response
