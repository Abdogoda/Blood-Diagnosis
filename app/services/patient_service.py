"""
Patient Management Service
Handles patient-related operations including patient-doctor relationships
"""
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Dict, Any, List
import random
import string

from app.database import User, DoctorInfo, doctor_patients
from app.services.ui_service import set_flash_message
from app.services.auth_service import hash_password


# ==================== Patient Creation ====================

def create_patient(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    gender: str,
    address: str,
    blood_type: str,
    dob: str,
    db: Session,
    redirect_url: str,
    doctor_id: int = None
) -> Dict[str, Any]:
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        response = RedirectResponse(url=redirect_url, status_code=303)
        set_flash_message(response, "error", "A user with this email already exists")
        return response
    
    # Generate username from email
    username = email.split('@')[0]
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
        password=hash_password(temp_password),
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
        
        # Link to doctor if doctor_id is provided
        if doctor_id:
            db.execute(
                doctor_patients.insert().values(
                    doctor_id=doctor_id,
                    patient_id=new_patient.id
                )
            )
            db.commit()
        
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


# ==================== Patient-Doctor Relationships ====================

def get_patient_doctors(patient_id: int, db: Session) -> List[Dict[str, Any]]:
    # Get doctor IDs linked to this patient
    doctor_ids_query = select(doctor_patients.c.doctor_id).where(
        doctor_patients.c.patient_id == patient_id
    )
    doctor_ids = [row[0] for row in db.execute(doctor_ids_query).fetchall()]
    
    # Get doctor details
    connected_doctors = []
    if doctor_ids:
        doctors = db.query(User).filter(
            User.id.in_(doctor_ids),
            User.role == "doctor"
        ).all()
        
        for doctor in doctors:
            doctor_info = db.query(DoctorInfo).filter(DoctorInfo.user_id == doctor.id).first()
            
            connected_doctors.append({
                "id": doctor.id,
                "name": f"Dr. {doctor.fname} {doctor.lname}",
                "fname": doctor.fname,
                "lname": doctor.lname,
                "email": doctor.email,
                "phone": doctor.phone,
                "specialization": doctor_info.specialization if doctor_info else "General",
                "license_number": doctor_info.license_number if doctor_info else "N/A",
                "profile_image": doctor.profile_image
            })
    
    return connected_doctors


def get_doctor_patients(doctor_id: int, db: Session) -> List[int]:
    patient_ids_query = select(doctor_patients.c.patient_id).where(
        doctor_patients.c.doctor_id == doctor_id
    )
    patient_ids = [row[0] for row in db.execute(patient_ids_query).fetchall()]
    return patient_ids


def link_patient_to_doctor(patient_id: int, doctor_id: int, db: Session) -> bool:
    try:
        # Check if already linked
        existing = db.execute(
            doctor_patients.select().where(
                doctor_patients.c.doctor_id == doctor_id,
                doctor_patients.c.patient_id == patient_id
            )
        ).first()
        
        if existing:
            return False
        
        # Create the link
        db.execute(
            doctor_patients.insert().values(
                doctor_id=doctor_id,
                patient_id=patient_id
            )
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def unlink_patient_from_doctor(patient_id: int, doctor_id: int, db: Session) -> bool:
    try:
        result = db.execute(
            doctor_patients.delete().where(
                doctor_patients.c.doctor_id == doctor_id,
                doctor_patients.c.patient_id == patient_id
            )
        )
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        return False


def is_patient_linked_to_doctor(patient_id: int, doctor_id: int, db: Session) -> bool:
    try:
        existing = db.execute(
            doctor_patients.select().where(
                doctor_patients.c.doctor_id == doctor_id,
                doctor_patients.c.patient_id == patient_id
            )
        ).first()
        return existing is not None
    except Exception:
        return False
