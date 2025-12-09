# Patients router
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.services import (
    require_role,
    set_flash_message,
    get_patient_doctors,
    cbc_prediction_service,
    blood_image_service,
    verify_password,
    hash_password
)
from app.services.profile_service import (
    update_user_profile,
    change_user_password,
    upload_user_profile_image
)
from app.services.medical_history_service import get_patient_medical_history
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
    # Get all medical history and limit to 3 most recent for dashboard
    all_medical_history = get_patient_medical_history(current_user.id, db)
    recent_medical_history = all_medical_history[:3] if all_medical_history else []
    
    stats = {
        "total_tests": 12,
        "pending_results": 2,
        "last_test_date": "2025-12-01",
        "medical_records": len(all_medical_history)
    }
    recent_tests = [
        {"date": "2025-12-01", "test_type": "CBC Analysis", "status": "Completed", "result": "Normal"},
        {"date": "2025-11-15", "test_type": "Blood Smear", "status": "Completed", "result": "Normal"},
    ]
    return templates.TemplateResponse("patient/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "recent_tests": recent_tests,
        "medical_history": recent_medical_history,
        "total_records": len(all_medical_history)
    })

@router.get("/medical-history")
async def patient_medical_history(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """Patient's medical history page"""
    medical_history = get_patient_medical_history(current_user.id, db)
    
    return templates.TemplateResponse("patient/medical_history.html", {
        "request": request,
        "current_user": current_user,
        "medical_history": medical_history
    })

@router.get("/reports")
async def patient_reports(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    """Patient's test reports page"""
    from app.database import Test
    
    # Get all tests for the patient
    tests = db.query(Test).filter(
        Test.patient_id == current_user.id
    ).order_by(Test.created_at.desc()).all()
    
    test_reports = []
    for test in tests:
        reviewer = db.query(User).filter(User.id == test.reviewed_by).first() if test.reviewed_by else None
        test_reports.append({
            "id": test.id,
            "result": test.result or "Pending",
            "date": test.created_at.strftime("%b %d, %Y"),
            "time": test.created_at.strftime("%I:%M %p"),
            "review_status": test.review_status,
            "confidence": float(test.confidence) if test.confidence else None,
            "comment": test.comment,
            "notes": test.notes,
            "reviewed_by": f"Dr. {reviewer.fname} {reviewer.lname}" if reviewer else None,
            "reviewed_at": test.reviewed_at.strftime("%b %d, %Y") if test.reviewed_at else None
        })
    
    return templates.TemplateResponse("patient/reports.html", {
        "request": request,
        "current_user": current_user,
        "reports": test_reports
    })

@router.get("/upload-test")
async def upload_test_page(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"]))
):
    return templates.TemplateResponse("shared/upload_test.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_patient.html",
        "back_url": "/patient/dashboard",
        "cbc_url": "/patient/upload-cbc",
        "image_url": "/patient/upload-image"
    })

@router.get("/upload-cbc")
async def upload_cbc_page(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"]))
):
    return templates.TemplateResponse("shared/upload_cbc.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_patient.html",
        "back_url": "/patient/upload-test",
        "csv_action": "/patient/upload-cbc-csv",
        "manual_action": "/patient/upload-cbc-manual"
    })

@router.post("/upload-cbc-csv")
async def upload_cbc_csv(
    request: Request,
    file: UploadFile = File(...),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    result = cbc_prediction_service.process_csv_upload(
        file=file,
        patient_id=current_user.id,
        uploaded_by_id=current_user.id,
        notes=notes,
        db=db
    )
    
    if not result["success"]:
        response = RedirectResponse(url="/patient/upload-cbc", status_code=303)
        set_flash_message(response, "error", result["message"])
        return response
    
    # Display results
    return templates.TemplateResponse("shared/cbc_result.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_patient.html",
        "back_url": "/patient/upload-cbc",
        "results": result["results"],
        "notes": result.get("notes")
    })

@router.post("/upload-cbc-manual")
async def upload_cbc_manual(
    request: Request,
    rbc: float = Form(...),
    hgb: float = Form(...),
    pcv: float = Form(...),
    mcv: float = Form(...),
    mch: float = Form(...),
    mchc: float = Form(...),
    tlc: float = Form(...),
    plt: float = Form(...),
    notes: str = Form(None),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    result = cbc_prediction_service.process_manual_input(
        rbc=rbc, hgb=hgb, pcv=pcv, mcv=mcv, mch=mch, mchc=mchc, tlc=tlc, plt=plt,
        patient_id=current_user.id,
        uploaded_by_id=current_user.id,
        notes=notes,
        db=db
    )
    
    if not result["success"]:
        response = RedirectResponse(url="/patient/upload-cbc", status_code=303)
        set_flash_message(response, "error", result["message"])
        return response
    
    # Display results (manual input returns single result)
    return templates.TemplateResponse("shared/cbc_result.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_patient.html",
        "back_url": "/patient/upload-cbc",
        "results": [result["result"]],  # Wrap in list for consistent template
        "notes": result.get("notes")
    })

@router.get("/upload-image")
async def upload_image_page(
    request: Request,
    current_user: User = Depends(require_role(["patient", "admin"]))
):
    return templates.TemplateResponse("shared/upload_image.html", {
        "request": request,
        "current_user": current_user,
        "base_layout": "layouts/base_patient.html",
        "back_url": "/patient/upload-test",
        "form_action": "/patient/upload-blood-image"
    })

@router.post("/upload-blood-image")
async def upload_blood_image(
    request: Request,
    file: UploadFile = File(...),
    description: str = Form(None),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    result = blood_image_service.process_image_upload(
        file=file,
        patient_id=current_user.id,
        uploaded_by_id=current_user.id,
        description=description,
        db=db
    )
    
    response = RedirectResponse(url="/patient/dashboard", status_code=303)
    set_flash_message(response, "success" if result["success"] else "error", result["message"])
    return response

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
    # Get doctors connected to this patient
    connected_doctors = get_patient_doctors(current_user.id, db)
    
    return templates.TemplateResponse("patient/account.html", {
        "request": request,
        "current_user": current_user,
        "patient": current_user,
        "phone": current_user.phone,
        "connected_doctors": connected_doctors
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
    address: str = Form(None),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    success, message = await update_user_profile(
        current_user=current_user,
        db=db,
        fname=fname,
        lname=lname,
        email=email,
        phone=phone,
        address=address,
        redirect_url="/patient/account"
    )
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
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
    success, message = await change_user_password(
        current_user=current_user,
        db=db,
        current_password=current_password,
        new_password=new_password,
        confirm_password=confirm_password
    )
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
    return response


@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: User = Depends(require_role(["patient", "admin"])),
    db: Session = Depends(get_db)
):
    success, message = await upload_user_profile_image(
        current_user=current_user,
        db=db,
        profile_image=profile_image
    )
    
    response = RedirectResponse(url="/patient/account", status_code=303)
    set_flash_message(response, "success" if success else "error", message)
    return response
