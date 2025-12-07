# Admin router for admin-specific routes
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services.auth_dependencies import require_role
from app.services.flash_messages import set_flash_message
import bcrypt
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

# Password hashing using bcrypt directly
def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')



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
    search: str = None,
    specialization: str = None,
    status: str = None,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(User).filter(User.role == "doctor")
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.fname.ilike(search_filter)) |
            (User.lname.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    if specialization and specialization != "all":
        from app.database import DoctorInfo
        query = query.join(DoctorInfo).filter(DoctorInfo.specialization == specialization)
    
    if status and status != "all":
        is_active = 1 if status == "active" else 0
        query = query.filter(User.is_active == is_active)
    
    doctors_query = query.order_by(User.created_at.desc()).all()
    
    doctors = [
        {
            "id": d.id,
            "initials": f"{d.fname[0]}{d.lname[0]}",
            "name": f"Dr. {d.fname} {d.lname}",
            "email": d.email,
            "specialization": d.doctor_info.specialization if d.doctor_info else "N/A",
            "license": d.doctor_info.license_number if d.doctor_info else "N/A",
            "patient_count": 0,  # Will be implemented when patient assignments are added
            "is_active": d.is_active
        }
        for d in doctors_query
    ]
    
    # Get unique specializations for filter dropdown
    from app.database import DoctorInfo
    specializations_query = db.query(DoctorInfo.specialization).distinct().all()
    unique_specs = [s[0] for s in specializations_query if s[0]]
    
    return templates.TemplateResponse("admin/doctors.html", {
        "request": request,
        "current_user": current_user,
        "doctors": doctors,
        "specializations": unique_specs,
        "search": search or "",
        "selected_specialization": specialization or "all",
        "selected_status": status or "all"
    })


@router.get("/doctors/{doctor_id}")
def view_doctor(
    request: Request,
    doctor_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    
    if not doctor:
        response = RedirectResponse(url="/admin/doctors", status_code=303)
        set_flash_message(response, "error", "Doctor not found")
        return response
    
    return templates.TemplateResponse("admin/doctor_detail.html", {
        "request": request,
        "current_user": current_user,
        "doctor": doctor
    })


@router.post("/doctors/add")
async def add_doctor(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    gender: str = Form(...),
    blood_type: str = Form(None),
    phone: str = Form(...),
    address: str = Form(None),
    specialization: str = Form(...),
    license_number: str = Form(...),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Check if email or username already exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing_user:
        response = RedirectResponse(url="/admin/doctors", status_code=303)
        set_flash_message(response, "error", "Email or username already exists")
        return response
    
    # Create new doctor user
    new_doctor = User(
        fname=fname,
        lname=lname,
        email=email,
        username=username,
        password=get_password_hash(password),
        gender=gender,
        blood_type=blood_type,
        phone=phone,
        address=address,
        role="doctor",
        is_active=1
    )
    
    db.add(new_doctor)
    db.flush()
    
    # Add doctor info
    from app.database import DoctorInfo
    
    doctor_info = DoctorInfo(
        user_id=new_doctor.id,
        specialization=specialization,
        license_number=license_number
    )
    db.add(doctor_info)
    
    db.commit()
    
    response = RedirectResponse(url="/admin/doctors", status_code=303)
    set_flash_message(response, "success", f"Doctor {fname} {lname} added successfully!")
    return response





@router.post("/doctors/{doctor_id}/toggle-status")
async def toggle_doctor_status(
    request: Request,
    doctor_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    
    if not doctor:
        response = RedirectResponse(url="/admin/doctors", status_code=303)
        set_flash_message(response, "error", "Doctor not found")
        return response
    
    # Toggle active status (using 1/0 for integer column)
    doctor.is_active = 0 if doctor.is_active == 1 else 1
    
    db.commit()
    
    status_text = "activated" if doctor.is_active == 1 else "deactivated"
    response = RedirectResponse(url="/admin/doctors", status_code=303)
    set_flash_message(response, "success", f"Doctor {doctor.fname} {doctor.lname} {status_text} successfully!")
    return response


@router.get("/patients")
def admin_patients(
    request: Request,
    search: str = "",
    blood_type: str = "all",
    status: str = "all",
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    from app.database import Test
    
    # Base query
    query = db.query(User).filter(User.role == "patient")
    
    # Search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.fname.ilike(search_filter)) |
            (User.lname.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    # Blood type filter
    if blood_type and blood_type != "all":
        query = query.filter(User.blood_type == blood_type)
    
    # Status filter
    if status == "active":
        query = query.filter(User.is_active == 1)
    elif status == "inactive":
        query = query.filter(User.is_active == 0)
    
    patients_query = query.all()
    
    # Get available blood types
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    patients = [
        {
            "id": p.id,
            "initials": f"{p.fname[0]}{p.lname[0]}",
            "name": f"{p.fname} {p.lname}",
            "email": p.email,
            "blood_type": p.blood_type or "N/A",
            "test_count": db.query(Test).filter(Test.patient_id == p.id).count(),
            "joined": p.created_at.strftime("%b %d, %Y"),
            "is_active": p.is_active == 1
        }
        for p in patients_query
    ]
    
    return templates.TemplateResponse("admin/patients.html", {
        "request": request,
        "current_user": current_user,
        "patients": patients,
        "search": search,
        "blood_types": blood_types,
        "selected_blood_type": blood_type,
        "selected_status": status
    })


@router.get("/patients/{patient_id}")
def view_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    
    if not patient:
        response = RedirectResponse(url="/admin/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    return templates.TemplateResponse("admin/patient_detail.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient
    })


@router.get("/patients/{patient_id}/reports")
def view_patient_reports(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    from app.database import Test, TestResult, TestFile
    
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    
    if not patient:
        response = RedirectResponse(url="/admin/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    # Get all tests for this patient
    tests = db.query(Test).filter(Test.patient_id == patient_id).order_by(Test.test_time.desc()).all()
    
    # Format tests with their results and files
    formatted_tests = []
    for test in tests:
        results = db.query(TestResult).filter(TestResult.test_id == test.id).all()
        files = db.query(TestFile).filter(TestFile.test_id == test.id).all()
        
        formatted_tests.append({
            "id": test.id,
            "name": test.name,
            "description": test.description,
            "test_time": test.test_time.strftime("%b %d, %Y at %I:%M %p"),
            "results_count": len(results),
            "files_count": len(files),
            "results": results,
            "files": files
        })
    
    return templates.TemplateResponse("admin/patient_reports.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "tests": formatted_tests
    })


@router.post("/patients/{patient_id}/toggle-status")
def toggle_patient_status(
    patient_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    
    if not patient:
        response = RedirectResponse(url="/admin/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    # Toggle status
    patient.is_active = 0 if patient.is_active == 1 else 1
    db.commit()
    
    status_text = "activated" if patient.is_active == 1 else "deactivated"
    response = RedirectResponse(url="/admin/patients", status_code=303)
    set_flash_message(response, "success", f"Patient {patient.fname} {patient.lname} has been {status_text}")
    return response


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
    return templates.TemplateResponse("admin/account.html", {
        "request": request,
        "current_user": current_user,
        "admin": current_user,
        "phone": current_user.phone
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
    current_user.phone = phone
    
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


@router.get("/settings")
def system_settings(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # Get system statistics
    total_users = db.query(User).count()
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    total_patients = db.query(User).filter(User.role == "patient").count()
    
    # System settings (these would typically be stored in a database or config file)
    settings = {
        "site_name": "Blood Diagnosis System",
        "site_description": "AI-powered blood analysis and diagnosis system",
        "maintenance_mode": False,
        "allow_registration": True,
        "require_email_verification": False,
        "max_upload_size": 10,  # MB
        "session_timeout": 60,  # minutes
        "enable_notifications": True,
        "enable_ai_predictions": True,
        "ai_confidence_threshold": 0.85,
        "backup_enabled": True,
        "backup_frequency": "daily",
    }
    
    stats = {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "disk_usage": "2.3 GB",
        "database_size": "156 MB",
        "uptime": "15 days"
    }
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "current_user": current_user,
        "settings": settings,
        "stats": stats
    })


@router.post("/settings/update")
async def update_system_settings(
    request: Request,
    site_name: str = Form(...),
    site_description: str = Form(...),
    maintenance_mode: bool = Form(False),
    allow_registration: bool = Form(False),
    require_email_verification: bool = Form(False),
    max_upload_size: int = Form(...),
    session_timeout: int = Form(...),
    enable_notifications: bool = Form(False),
    enable_ai_predictions: bool = Form(False),
    ai_confidence_threshold: float = Form(...),
    backup_enabled: bool = Form(False),
    backup_frequency: str = Form(...),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    # In a real application, save these settings to a database or config file
    # For now, just show a success message
    
    response = RedirectResponse(url="/admin/settings", status_code=303)
    set_flash_message(response, "success", "System settings updated successfully!")
    return response
