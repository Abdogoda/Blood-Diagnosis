# Doctors router
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

router = APIRouter(prefix="/doctor", tags=["doctors"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def doctor_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get actual patient count
    total_patients = db.query(User).filter(User.role == "patient", User.is_active == 1).count()
    
    stats = {
        "total_patients": total_patients,
        "pending_reports": 0,
        "urgent_cases": 0,
        "completed_today": 0
    }
    
    # Get recent patients (users with role='patient')
    recent_patients_query = db.query(User).filter(User.role == "patient", User.is_active == 1).order_by(User.created_at.desc()).limit(5).all()
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

@router.get("/patients")
async def patients_list(
    request: Request,
    search: str = None,
    blood_type: str = None,
    gender: str = None,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Build query for patients
    query = db.query(User).filter(User.role == "patient", User.is_active == 1)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.fname.ilike(search_term)) | 
            (User.lname.ilike(search_term)) | 
            (User.email.ilike(search_term))
        )
    
    if blood_type:
        query = query.filter(User.blood_type == blood_type)
    
    if gender:
        query = query.filter(User.gender == gender)
    
    # Get patients
    patients = query.order_by(User.created_at.desc()).all()
    
    return templates.TemplateResponse("doctor/patients.html", {
        "request": request,
        "current_user": current_user,
        "patients": patients,
        "search": search,
        "selected_blood_type": blood_type,
        "selected_gender": gender
    })

@router.get("/add-patient")
async def add_patient_page(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"]))
):
    return templates.TemplateResponse("shared/add_patient.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_doctor.html",
        "back_url": "/doctor/patients",
        "form_action": "/doctor/patient/add"
    })

@router.post("/patient/add")
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
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.patient_service import add_patient_logic
    
    result = add_patient_logic(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        gender=gender,
        address=address,
        blood_type=blood_type,
        dob=dob,
        db=db,
        redirect_url="/doctor/add-patient"
    )
    
    if isinstance(result, RedirectResponse):
        return result
    
    if result["success"]:
        response = RedirectResponse(url=f"/doctor/patient/{result['patient_id']}", status_code=303)
        set_flash_message(response, "success", f"Patient {result['name']} added successfully! Temporary password: {result['temp_password']}")
        return response
    else:
        response = RedirectResponse(url="/doctor/add-patient", status_code=303)
        set_flash_message(response, "error", f"Error adding patient: {result['error']}")
        return response

@router.get("/patient/{patient_id}")
async def patient_profile(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.database import MedicalHistory, Test
    
    # Get patient user
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        return templates.TemplateResponse("doctor/dashboard.html", {
            "request": request,
            "current_user": current_user,
            "error": "Patient not found"
        }, status_code=404)
    
    # Get patient phone
    phone = patient.phone
    
    # Get medical history ordered from oldest to latest
    medical_history_query = db.query(MedicalHistory).filter(
        MedicalHistory.patient_id == patient_id
    ).order_by(MedicalHistory.diagnosis_date.asc()).all()
    
    medical_history = []
    for record in medical_history_query:
        doctor = db.query(User).filter(User.id == record.doctor_id).first() if record.doctor_id else None
        medical_history.append({
            "id": record.id,
            "condition": record.medical_condition,
            "date": record.diagnosis_date.strftime("%b %d, %Y"),
            "treatment": record.treatment,
            "notes": record.notes,
            "doctor_name": f"Dr. {doctor.fname} {doctor.lname}" if doctor else "Unknown"
        })
    
    # Get recent tests
    recent_tests_query = db.query(Test).filter(
        Test.patient_id == patient_id
    ).order_by(Test.test_time.desc()).limit(5).all()
    
    recent_tests = [
        {
            "id": test.id,
            "name": test.name,
            "date": test.test_time.strftime("%b %d, %Y")
        }
        for test in recent_tests_query
    ]
    
    return templates.TemplateResponse("doctor/patient_profile.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "phone": phone,
        "medical_history": medical_history,
        "recent_tests": recent_tests
    })

@router.get("/upload-test/{patient_id}")
async def upload_test_page(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    return templates.TemplateResponse("shared/upload_test.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "base_layout": "layouts/base_doctor.html",
        "back_url": "/doctor/patients",
        "cbc_url": f"/doctor/upload-cbc/{patient_id}",
        "image_url": f"/doctor/upload-image/{patient_id}"
    })

@router.get("/upload-cbc/{patient_id}")
async def upload_cbc_page(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    return templates.TemplateResponse("shared/upload_cbc.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "base_layout": "layouts/base_doctor.html",
        "back_url": f"/doctor/upload-test/{patient_id}",
        "csv_action": f"/doctor/upload-cbc-csv/{patient_id}",
        "manual_action": f"/doctor/upload-cbc-manual/{patient_id}"
    })

@router.post("/upload-cbc-csv/{patient_id}")
async def upload_cbc_csv(
    request: Request,
    patient_id: int,
    file: UploadFile = File(...),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.patient_service import upload_cbc_csv_logic
    
    result = upload_cbc_csv_logic(
        file=file,
        notes=notes,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        db=db
    )
    
    response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    set_flash_message(response, "success" if result["success"] else "error", result["message"])
    return response

@router.post("/upload-cbc-manual/{patient_id}")
async def upload_cbc_manual(
    request: Request,
    patient_id: int,
    rbc: float = Form(...),
    hgb: float = Form(...),
    pcv: float = Form(...),
    mcv: float = Form(...),
    mch: float = Form(...),
    mchc: float = Form(...),
    tlc: float = Form(...),
    plt: float = Form(...),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.patient_service import upload_cbc_manual_logic
    
    result = upload_cbc_manual_logic(
        rbc=rbc, hgb=hgb, pcv=pcv, mcv=mcv, mch=mch, mchc=mchc, tlc=tlc, plt=plt,
        notes=notes,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        db=db
    )
    
    response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    set_flash_message(response, "success" if result["success"] else "error", result["message"])
    return response

@router.get("/upload-image/{patient_id}")
async def upload_image_page(
    request: Request,
    patient_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    return templates.TemplateResponse("shared/upload_image.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "base_layout": "layouts/base_doctor.html",
        "back_url": f"/doctor/upload-test/{patient_id}",
        "form_action": f"/doctor/upload-blood-image/{patient_id}"
    })

@router.post("/upload-blood-image/{patient_id}")
async def upload_blood_image(
    request: Request,
    patient_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.services.patient_service import upload_blood_image_logic
    
    result = upload_blood_image_logic(
        file=file,
        description=description,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        db=db
    )
    
    response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    set_flash_message(response, "success" if result["success"] else "error", result["message"])
    return response

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
    phone = current_user.phone
    
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
    address: str = Form(None),
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
    current_user.phone = phone
    current_user.address = address
    
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


@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_ext = os.path.splitext(profile_image.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        response = RedirectResponse(url="/doctor/account", status_code=303)
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
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success", "Profile image updated successfully!")
    return response
