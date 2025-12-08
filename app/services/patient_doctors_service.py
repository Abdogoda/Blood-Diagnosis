"""
Service for managing patient-doctor relationships
Provides reusable functions to get connected doctors for patients
"""
from sqlalchemy.orm import Session
from app.database import User, doctor_patients
from sqlalchemy import select
from typing import List, Dict, Any


def get_patient_doctors(patient_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Get all doctors connected to a specific patient
    
    Args:
        patient_id: The ID of the patient
        db: Database session
        
    Returns:
        List of dictionaries containing doctor information
    """
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
            # Get doctor info with specialization
            from app.database import DoctorInfo
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
