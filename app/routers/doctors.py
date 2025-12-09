# Doctors router
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services import (
    require_role,
    set_flash_message,
    create_patient,
    get_patient_doctors,
    cbc_prediction_service,
    blood_image_service,
)
from app.services.profile_service import (
    update_doctor_profile,
    change_user_password,
    upload_user_profile_image
)
from app.services.medical_history_service import (
    create_diagnosis,
    get_patient_medical_history,
    update_diagnosis,
    delete_diagnosis
)

router = APIRouter(prefix="/doctor", tags=["doctors"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def doctor_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.database import doctor_patients, Test
    from sqlalchemy import select
    
    # Get patient count based on role
    if current_user.role == "doctor":
        # Get only linked patients count
        patient_ids_query = select(doctor_patients.c.patient_id).where(
            doctor_patients.c.doctor_id == current_user.id
        )
        patient_ids = [row[0] for row in db.execute(patient_ids_query).fetchall()]
        total_patients = db.query(User).filter(
            User.role == "patient", 
            User.is_active == 1,
            User.id.in_(patient_ids) if patient_ids else False
        ).count()
        
        # Get recent linked patients only
        recent_patients_query = db.query(User).filter(
            User.role == "patient", 
            User.is_active == 1,
            User.id.in_(patient_ids) if patient_ids else False
        ).order_by(User.created_at.desc()).limit(5).all()
        
        # Get pending tests count for linked patients
        pending_reports = db.query(Test).filter(
            Test.patient_id.in_(patient_ids) if patient_ids else False,
            Test.review_status == 'pending'
        ).count()
        
        # Get review requests for this doctor
        review_requests = db.query(Test).filter(
            Test.review_requested_from == current_user.id,
            Test.review_status == 'pending'
        ).order_by(Test.review_requested_at.desc()).limit(5).all()
        
        review_requests_list = []
        for test in review_requests:
            patient = db.query(User).filter(User.id == test.patient_id).first()
            review_requests_list.append({
                "test_id": test.id,
                "patient_name": f"{patient.fname} {patient.lname}",
                "patient_id": patient.id,
                "requested_at": test.review_requested_at.strftime("%b %d, %Y") if test.review_requested_at else "N/A",
                "notes": test.notes or "No notes"
            })
    else:
        # Admin sees all patients
        total_patients = db.query(User).filter(User.role == "patient").count()
        recent_patients_query = db.query(User).filter(User.role == "patient").order_by(User.created_at.desc()).limit(5).all()
        
        # Get all pending tests
        pending_reports = db.query(Test).filter(Test.review_status == 'pending').count()
        review_requests_list = []
    
    stats = {
        "total_patients": total_patients,
        "pending_reports": pending_reports,
        "completed_today": 0,
        "review_requests": len(review_requests_list)
    }
    
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
        "recent_patients": recent_patients,
        "review_requests": review_requests_list
    })

@router.get("/patients")
async def patients_list(
    request: Request,
    search: str = None,
    blood_type: str = None,
    gender: str = None,
    my_patients: str = None,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    from app.database import doctor_patients
    from sqlalchemy import select
    
    # Build query for patients
    query = db.query(User).filter(User.role == "patient")
    
    # Filter by doctor's patients only
    if my_patients == "true" and current_user.role == "doctor":
        # Get patient IDs linked to this doctor
        patient_ids_query = select(doctor_patients.c.patient_id).where(
            doctor_patients.c.doctor_id == current_user.id
        )
        patient_ids = [row[0] for row in db.execute(patient_ids_query).fetchall()]
        query = query.filter(User.id.in_(patient_ids))
    
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
    
    # Get patient IDs linked to current doctor (for displaying link status)
    doctor_patient_ids = []
    if current_user.role == "doctor":
        patient_ids_query = select(doctor_patients.c.patient_id).where(
            doctor_patients.c.doctor_id == current_user.id
        )
        doctor_patient_ids = [row[0] for row in db.execute(patient_ids_query).fetchall()]
    
    return templates.TemplateResponse("doctor/patients.html", {
        "request": request,
        "current_user": current_user,
        "patients": patients,
        "search": search,
        "selected_blood_type": blood_type,
        "selected_gender": gender,
        "my_patients": my_patients,
        "doctor_patient_ids": doctor_patient_ids
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
        redirect_url="/doctor/add-patient",
        doctor_id=current_user.id  # Link patient to this doctor
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
    from app.database import Test
    
    # Get patient user
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        return templates.TemplateResponse("doctor/dashboard.html", {
            "request": request,
            "current_user": current_user,
            "error": "Patient not found"
        }, status_code=404)
    
    # Check if patient is linked to this doctor
    is_linked = False
    if current_user.role == "admin":
        is_linked = True
    else:
        is_linked = patient in current_user.patients
    
    # Get patient phone
    phone = patient.phone
    
    # Get connected doctors for this patient
    connected_doctors = get_patient_doctors(patient_id, db)
    
    # Get medical history using service
    medical_history = get_patient_medical_history(patient_id, db)
    
    # Get recent tests
    recent_tests_query = db.query(Test).filter(
        Test.patient_id == patient_id
    ).order_by(Test.created_at.desc()).limit(5).all()
    
    recent_tests = [
        {
            "id": test.id,
            "result": test.result or "Pending",
            "date": test.created_at.strftime("%b %d, %Y"),
            "review_status": test.review_status
        }
        for test in recent_tests_query
    ]
    
    return templates.TemplateResponse("doctor/patient_profile.html", {
        "request": request,
        "current_user": current_user,
        "patient": patient,
        "phone": phone,
        "connected_doctors": connected_doctors,
        "medical_history": medical_history,
        "recent_tests": recent_tests,
        "is_linked": is_linked
    })

@router.post("/patient/{patient_id}/link")
async def link_patient(
    patient_id: int,
    current_user: User = Depends(require_role(["doctor"])),
    db: Session = Depends(get_db)
):
    """Link a patient to the current doctor"""
    from app.database import doctor_patients
    from sqlalchemy.exc import IntegrityError
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    try:
        # Check if already linked
        existing = db.execute(
            doctor_patients.select().where(
                doctor_patients.c.doctor_id == current_user.id,
                doctor_patients.c.patient_id == patient_id
            )
        ).first()
        
        if existing:
            response = RedirectResponse(url="/doctor/patients", status_code=303)
            set_flash_message(response, "info", f"{patient.fname} {patient.lname} is already linked to you")
            return response
        
        # Create the link
        db.execute(
            doctor_patients.insert().values(
                doctor_id=current_user.id,
                patient_id=patient_id
            )
        )
        db.commit()
        
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "success", f"Successfully linked {patient.fname} {patient.lname} to your account")
        return response
        
    except IntegrityError:
        db.rollback()
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Failed to link patient")
        return response

@router.post("/patient/{patient_id}/unlink")
async def unlink_patient(
    patient_id: int,
    current_user: User = Depends(require_role(["doctor"])),
    db: Session = Depends(get_db)
):
    """Unlink a patient from the current doctor"""
    from app.database import doctor_patients
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    try:
        # Delete the link
        result = db.execute(
            doctor_patients.delete().where(
                doctor_patients.c.doctor_id == current_user.id,
                doctor_patients.c.patient_id == patient_id
            )
        )
        db.commit()
        
        if result.rowcount == 0:
            response = RedirectResponse(url="/doctor/patients", status_code=303)
            set_flash_message(response, "info", f"{patient.fname} {patient.lname} was not linked to you")
            return response
        
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "success", f"Successfully unlinked {patient.fname} {patient.lname} from your account")
        return response
        
    except Exception as e:
        db.rollback()
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Failed to unlink patient")
        return response

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
    
    # Check patient access using policy service
    from app.services.policy_service import require_patient_access
    access_error = require_patient_access(request, current_user, patient, db)
    if access_error:
        return access_error
    
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
    
    # Check patient access using policy service
    from app.services.policy_service import require_patient_access
    access_error = require_patient_access(request, current_user, patient, db)
    if access_error:
        return access_error
    
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
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    # Check patient access using policy service
    from app.services.policy_service import require_patient_access
    access_error = require_patient_access(request, current_user, patient, db)
    if access_error:
        return access_error
    
    result = cbc_prediction_service.process_csv_upload(
        file=file,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        notes=notes,
        db=db
    )
    
    if not result["success"]:
        response = RedirectResponse(url=f"/doctor/upload-cbc/{patient_id}", status_code=303)
        set_flash_message(response, "error", result["message"])
        return response
    
    # Redirect to test detail page
    response = RedirectResponse(url=f"/doctor/test/{result['test_id']}", status_code=303)
    set_flash_message(response, "success", result["message"])
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
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
        set_flash_message(response, "error", "Patient not found")
        return response
    
    # Check patient access using policy service
    from app.services.policy_service import require_patient_access
    access_error = require_patient_access(request, current_user, patient, db)
    if access_error:
        return access_error
    
    result = cbc_prediction_service.process_manual_input(
        rbc=rbc, hgb=hgb, pcv=pcv, mcv=mcv, mch=mch, mchc=mchc, tlc=tlc, plt=plt,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        notes=notes,
        db=db
    )
    
    if not result["success"]:
        response = RedirectResponse(url=f"/doctor/upload-cbc/{patient_id}", status_code=303)
        set_flash_message(response, "error", result["message"])
        return response
    
    # Redirect to test detail page
    response = RedirectResponse(url=f"/doctor/test/{result['test_id']}", status_code=303)
    set_flash_message(response, "success", result["message"])
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
    
    # Check patient access using policy service
    from app.services.policy_service import require_patient_access
    access_error = require_patient_access(request, current_user, patient, db)
    if access_error:
        return access_error
    

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
    result = blood_image_service.process_image_upload(
        file=file,
        patient_id=patient_id,
        uploaded_by_id=current_user.id,
        description=description,
        db=db
    )
    
    response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    set_flash_message(response, "success" if result["success"] else "error", result["message"])
    return response

@router.get("/test/{test_id}")
async def view_test(
    request: Request,
    test_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """View test details for review"""
    from app.database import Test, TestFile, doctor_patients, Model
    from datetime import datetime
    
    # Get the test
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        response = RedirectResponse(url="/doctor/dashboard", status_code=303)
        set_flash_message(response, "error", "Test not found")
        return response
    
    # Get patient info
    patient = db.query(User).filter(User.id == test.patient_id).first()
    
    # Check if doctor has access to this patient
    if current_user.role == "doctor":
        is_linked = patient in current_user.patients
        if not is_linked:
            response = RedirectResponse(url="/doctor/dashboard", status_code=303)
            set_flash_message(response, "error", "You don't have access to this patient's tests")
            return response
    
    # Get test files
    test_files = db.query(TestFile).filter(TestFile.test_id == test_id).all()
    
    # Load CSV data if exists
    csv_data = None
    csv_file = None
    for file in test_files:
        if file.extension == '.csv' and file.type == 'output':
            csv_file = file
            try:
                import pandas as pd
                from app.ai.cbc import build_report
                df = pd.read_csv(file.path)
                csv_data = df.to_dict('records')
                # Generate reports for each record
                for record in csv_data:
                    record['medical_report'] = build_report(record)
            except Exception as e:
                print(f"Error loading CSV: {e}")
                csv_data = None
            break
    
    # Get reviewer info if reviewed
    reviewer = None
    if test.reviewed_by:
        reviewer = db.query(User).filter(User.id == test.reviewed_by).first()
    
    # Get model name for test type
    model_name = None
    if test.model_id:
        model = db.query(Model).filter(Model.id == test.model_id).first()
        if model:
            model_name = model.name
    
    return templates.TemplateResponse("doctor/test_detail.html", {
        "request": request,
        "current_user": current_user,
        "test": test,
        "patient": patient,
        "test_files": test_files,
        "csv_data": csv_data,
        "csv_file": csv_file,
        "reviewer": reviewer,
        "model_name": model_name
    })

@router.post("/test/{test_id}/review")
async def review_test(
    request: Request,
    test_id: int,
    review_status: str = Form(...),
    comment: str = Form(None),
    result: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """Update test review status"""
    from app.database import Test, doctor_patients
    from datetime import datetime
    
    # Get the test
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        response = RedirectResponse(url="/doctor/dashboard", status_code=303)
        set_flash_message(response, "error", "Test not found")
        return response
    
    # Get patient info
    patient = db.query(User).filter(User.id == test.patient_id).first()
    
    # Check if doctor has access to this patient
    if current_user.role == "doctor":
        is_linked = patient in current_user.patients
        if not is_linked:
            response = RedirectResponse(url="/doctor/dashboard", status_code=303)
            set_flash_message(response, "error", "You don't have access to this patient's tests")
            return response
    
    # Validate review status
    if review_status not in ['accepted', 'rejected', 'pending']:
        response = RedirectResponse(url=f"/doctor/test/{test_id}", status_code=303)
        set_flash_message(response, "error", "Invalid review status")
        return response
    
    try:
        # Update test
        test.review_status = review_status
        test.reviewed_by = current_user.id
        test.reviewed_at = datetime.utcnow()
        if comment:
            test.comment = comment
        if result:
            test.result = result
        
        db.commit()
        
        response = RedirectResponse(url=f"/doctor/patient/{test.patient_id}", status_code=303)
        set_flash_message(response, "success", f"Test marked as {review_status}")
        return response
        
    except Exception as e:
        db.rollback()
        response = RedirectResponse(url=f"/doctor/test/{test_id}", status_code=303)
        set_flash_message(response, "error", f"Error updating test: {str(e)}")
        return response

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
    success, message = await update_doctor_profile(
        current_user=current_user,
        db=db,
        fname=fname,
        lname=lname,
        email=email,
        phone=phone,
        address=address,
        specialization=specialization,
        redirect_url="/doctor/account"
    )
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
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
    success, message = await change_user_password(
        current_user=current_user,
        db=db,
        current_password=current_password,
        new_password=new_password,
        confirm_password=confirm_password
    )
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
    return response


@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    success, message = await upload_user_profile_image(
        current_user=current_user,
        db=db,
        profile_image=profile_image
    )
    
    response = RedirectResponse(url="/doctor/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
    return response


@router.post("/patient/{patient_id}/diagnose")
async def add_diagnosis(
    request: Request,
    patient_id: int,
    medical_condition: str = Form(...),
    treatment: str = Form(None),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """Add a new diagnosis/medical history record for a patient"""
    success, message, record = create_diagnosis(
        patient_id=patient_id,
        doctor_id=current_user.id,
        medical_condition=medical_condition,
        treatment=treatment,
        notes=notes,
        db=db
    )
    
    response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
    return response


@router.post("/diagnosis/{record_id}/update")
async def update_diagnosis_record(
    request: Request,
    record_id: int,
    medical_condition: str = Form(...),
    treatment: str = Form(None),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """Update an existing diagnosis/medical history record"""
    success, message = update_diagnosis(
        record_id=record_id,
        doctor_id=current_user.id,
        medical_condition=medical_condition,
        treatment=treatment,
        notes=notes,
        db=db
    )
    
    # Get patient_id from the record to redirect back
    from app.database import MedicalHistory
    record = db.query(MedicalHistory).filter(MedicalHistory.id == record_id).first()
    patient_id = record.patient_id if record else None
    
    if patient_id:
        response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    else:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
    
    set_flash_message(response, "success" if success else "error", message)
    return response


@router.post("/diagnosis/{record_id}/delete")
async def delete_diagnosis_record(
    request: Request,
    record_id: int,
    current_user: User = Depends(require_role(["doctor", "admin"])),
    db: Session = Depends(get_db)
):
    """Delete a diagnosis/medical history record"""
    # Get patient_id before deleting
    from app.database import MedicalHistory
    record = db.query(MedicalHistory).filter(MedicalHistory.id == record_id).first()
    patient_id = record.patient_id if record else None
    
    success, message = delete_diagnosis(
        record_id=record_id,
        doctor_id=current_user.id,
        db=db
    )
    
    if patient_id:
        response = RedirectResponse(url=f"/doctor/patient/{patient_id}", status_code=303)
    else:
        response = RedirectResponse(url="/doctor/patients", status_code=303)
    
    set_flash_message(response, "success" if success else "error", message)
    return response
