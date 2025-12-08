# Admin router for admin-specific routes
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services import (
    require_role,
    set_flash_message,
    create_patient,
    get_patient_doctors,
    verify_password,
    hash_password
)
import os
import uuid
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")



@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func, extract
    from datetime import timedelta
    from app.database import Test
    
    total_users = db.query(User).count()
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    total_patients = db.query(User).filter(User.role == "patient").count()
    total_admins = db.query(User).filter(User.role == "admin").count()
    total_tests = db.query(Test).count()
    
    # Calculate active users (users created in the last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
    
    # Calculate user growth (percentage increase from previous period)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    previous_period_users = db.query(User).filter(
        User.created_at >= sixty_days_ago,
        User.created_at < thirty_days_ago
    ).count()
    
    growth_rate = 0
    if previous_period_users > 0:
        growth_rate = ((active_users - previous_period_users) / previous_period_users) * 100
    
    stats = {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_admins": total_admins,
        "total_tests": total_tests,
        "active_users": active_users,
        "growth_rate": round(growth_rate, 1),
        "model_accuracy": 99.5,
        "avg_processing_time": 2.3
    }
    
    # User Analytics - Registration trend for last 7 days
    registration_trend = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = db.query(User).filter(
            func.date(User.created_at) == day
        ).count()
        registration_trend.append({
            "date": day.strftime("%m/%d"),
            "count": count
        })
    
    # Role distribution
    role_distribution = {
        "admin": total_admins,
        "doctor": total_doctors,
        "patient": total_patients
    }
    
    # Gender distribution
    gender_stats = db.query(
        User.gender,
        func.count(User.id)
    ).filter(User.gender.isnot(None)).group_by(User.gender).all()
    
    gender_distribution = {gender: count for gender, count in gender_stats}
    
    # Blood type distribution
    blood_type_stats = db.query(
        User.blood_type,
        func.count(User.id)
    ).filter(User.blood_type.isnot(None)).group_by(User.blood_type).all()
    
    blood_type_distribution = {blood_type: count for blood_type, count in blood_type_stats}
    
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
        "recent_users": recent_users,
        "registration_trend": registration_trend,
        "role_distribution": role_distribution,
        "gender_distribution": gender_distribution,
        "blood_type_distribution": blood_type_distribution
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
        password=hash_password(password),
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
    
    patients_query = query.order_by(User.created_at.desc()).all()
    
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
    
    # Get connected doctors for this patient
    connected_doctors = get_patient_doctors(patient_id, db)
    
    return templates.TemplateResponse("admin/patient_detail.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "connected_doctors": connected_doctors
    })


@router.get("/patients/{patient_id}/reports")
def view_patient_reports(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    from app.database import Test, TestFile, Model
    
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    
    if not patient:
        response = RedirectResponse(url="/admin/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    # Get all tests for this patient
    tests = db.query(Test).filter(Test.patient_id == patient_id).order_by(Test.created_at.desc()).all()
    
    # Format tests with their files and review status
    formatted_tests = []
    for test in tests:
        files = db.query(TestFile).filter(TestFile.test_id == test.id).all()
        model = db.query(Model).filter(Model.id == test.model_id).first() if test.model_id else None
        reviewed_by_user = db.query(User).filter(User.id == test.reviewed_by).first() if test.reviewed_by else None
        
        formatted_tests.append({
            "id": test.id,
            "created_at": test.created_at.strftime("%b %d, %Y at %I:%M %p"),
            "result": test.result,
            "confidence": float(test.confidence) if test.confidence else None,
            "review_status": test.review_status,
            "reviewed_by": f"Dr. {reviewed_by_user.fname} {reviewed_by_user.lname}" if reviewed_by_user else None,
            "reviewed_at": test.reviewed_at.strftime("%b %d, %Y at %I:%M %p") if test.reviewed_at else None,
            "model": model.name if model else None,
            "notes": test.notes,
            "comment": test.comment,
            "files_count": len(files),
            "files": files
        })
    
    return templates.TemplateResponse("admin/patient_reports.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "tests": formatted_tests
    })


@router.get("/add-patient")
async def add_patient_page(
    request: Request,
    current_user: User = Depends(require_role(["admin"]))
):
    return templates.TemplateResponse("shared/add_patient.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_admin.html",
        "back_url": "/admin/patients",
        "form_action": "/admin/patients/add"
    })


@router.post("/patients/add")
async def add_patient(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    dob: str = Form(None),
    gender: str = Form(...),
    address: str = Form(None),
    blood_type: str = Form(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    result = create_patient(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        gender=gender,
        address=address,
        blood_type=blood_type,
        dob=dob,
        db=db,
        redirect_url="/admin/add-patient"
    )
    
    if isinstance(result, RedirectResponse):
        return result
    
    if result["success"]:
        response = RedirectResponse(url=f"/admin/patients/{result['patient_id']}", status_code=303)
        set_flash_message(response, "success", f"Patient {result['name']} added successfully! Temporary password: {result['temp_password']}")
        return response
    else:
        response = RedirectResponse(url="/admin/add-patient", status_code=303)
        set_flash_message(response, "error", f"Error adding patient: {result['error']}")
        return response


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
    address: str = Form(None),
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
    current_user.address = address
    
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
    current_user.password = hash_password(new_password)
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