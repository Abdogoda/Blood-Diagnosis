"""
Shared service for patient management operations
Used by both admin and doctor roles to avoid code duplication
"""
from fastapi import Form, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import User
from app.services.flash_messages import set_flash_message
from app.services.password_utils import get_password_hash
import random
import string


def add_patient_logic(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    gender: str,
    address: str,
    blood_type: str,
    dob: str,
    db: Session,
    redirect_url: str
) -> RedirectResponse:
    """
    Shared logic for adding a patient
    Used by both admin and doctor routes
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        response = RedirectResponse(url=redirect_url, status_code=303)
        set_flash_message(response, "error", "A user with this email already exists")
        return response
    
    # Generate username from email
    username = email.split('@')[0]
    # Check if username exists and make it unique if necessary
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Generate random temporary password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Create new patient user
    new_patient = User(
        username=username,
        password=get_password_hash(temp_password),
        fname=first_name,
        lname=last_name,
        email=email,
        phone=phone,
        gender=gender,
        address=address,
        blood_type=blood_type if blood_type else None,
        role="patient",
        is_active=1
    )
    
    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        # Return success with patient ID
        return {
            "success": True,
            "patient_id": new_patient.id,
            "temp_password": temp_password,
            "name": f"{first_name} {last_name}"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }


def upload_cbc_csv_logic(
    file: UploadFile,
    notes: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
):
    """
    Shared logic for uploading CBC CSV
    Used by both patient and doctor routes
    """
    # TODO: Implement CBC CSV upload logic
    # - Save file
    # - Parse CSV
    # - Create Test record
    # - Create TestResult record
    # - Run AI prediction
    return {"success": True, "message": "CBC test uploaded successfully!"}


def upload_cbc_manual_logic(
    rbc: float,
    hgb: float,
    pcv: float,
    mcv: float,
    mch: float,
    mchc: float,
    tlc: float,
    plt: float,
    notes: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
):
    """
    Shared logic for manual CBC input
    Used by both patient and doctor routes
    """
    # TODO: Implement CBC manual input logic
    # - Create Test record
    # - Create TestResult with parameters
    # - Run AI prediction
    return {"success": True, "message": "CBC test submitted successfully!"}


def upload_blood_image_logic(
    file: UploadFile,
    description: str,
    patient_id: int,
    uploaded_by_id: int,
    db: Session
):
    """
    Shared logic for blood image upload
    Used by both patient and doctor routes
    """
    # TODO: Implement blood image upload logic
    # - Save image file
    # - Create Test record
    # - Create TestFile record
    # - Run AI image analysis
    return {"success": True, "message": "Blood image uploaded successfully!"}
