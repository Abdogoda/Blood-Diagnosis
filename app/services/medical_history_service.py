"""Medical history management service for handling diagnosis records"""
from sqlalchemy.orm import Session
from app.database import User, MedicalHistory
from datetime import datetime


def create_diagnosis(
    patient_id: int,
    doctor_id: int,
    medical_condition: str,
    treatment: str = None,
    notes: str = None,
    db: Session = None
) -> tuple[bool, str, MedicalHistory]:
    """
    Create a new medical history/diagnosis record
    
    Args:
        patient_id: ID of the patient
        doctor_id: ID of the diagnosing doctor
        medical_condition: The medical condition/diagnosis
        treatment: Prescribed treatment (optional)
        notes: Additional notes (optional)
        db: Database session
        
    Returns:
        Tuple of (success: bool, message: str, record: MedicalHistory or None)
    """
    # Verify patient exists
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == "patient"
    ).first()
    
    if not patient:
        return False, "Patient not found", None
    
    # Verify doctor exists
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == "doctor"
    ).first()
    
    if not doctor:
        return False, "Doctor not found", None
    
    # Check if doctor has access to this patient
    if patient not in doctor.patients and doctor.role != "admin":
        return False, "You don't have access to this patient", None
    
    # Create medical history record
    medical_record = MedicalHistory(
        patient_id=patient_id,
        doctor_id=doctor_id,
        medical_condition=medical_condition,
        treatment=treatment,
        notes=notes,
        created_at=datetime.utcnow()
    )
    
    db.add(medical_record)
    db.commit()
    db.refresh(medical_record)
    
    return True, "Diagnosis record created successfully", medical_record


def get_patient_medical_history(
    patient_id: int,
    db: Session
) -> list:
    """
    Get all medical history records for a patient
    
    Args:
        patient_id: ID of the patient
        db: Database session
        
    Returns:
        List of formatted medical history records
    """
    medical_history_query = db.query(MedicalHistory).filter(
        MedicalHistory.patient_id == patient_id
    ).order_by(MedicalHistory.created_at.desc()).all()
    
    medical_history = []
    for record in medical_history_query:
        doctor = db.query(User).filter(User.id == record.doctor_id).first() if record.doctor_id else None
        medical_history.append({
            "id": record.id,
            "condition": record.medical_condition,
            "date": record.created_at.strftime("%b %d, %Y"),
            "treatment": record.treatment,
            "notes": record.notes,
            "doctor_name": f"Dr. {doctor.fname} {doctor.lname}" if doctor else "Unknown",
            "doctor_id": record.doctor_id
        })
    
    return medical_history


def update_diagnosis(
    record_id: int,
    doctor_id: int,
    medical_condition: str = None,
    treatment: str = None,
    notes: str = None,
    db: Session = None
) -> tuple[bool, str]:
    """
    Update an existing medical history record
    
    Args:
        record_id: ID of the medical history record
        doctor_id: ID of the doctor making the update
        medical_condition: Updated medical condition (optional)
        treatment: Updated treatment (optional)
        notes: Updated notes (optional)
        db: Database session
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    record = db.query(MedicalHistory).filter(MedicalHistory.id == record_id).first()
    
    if not record:
        return False, "Medical record not found"
    
    # Only the doctor who created the record can update it
    if record.doctor_id != doctor_id:
        return False, "You can only update your own diagnosis records"
    
    # Update fields if provided
    if medical_condition:
        record.medical_condition = medical_condition
    if treatment:
        record.treatment = treatment
    if notes:
        record.notes = notes
    
    db.commit()
    
    return True, "Diagnosis record updated successfully"


def delete_diagnosis(
    record_id: int,
    doctor_id: int,
    db: Session
) -> tuple[bool, str]:
    """
    Delete a medical history record
    
    Args:
        record_id: ID of the medical history record
        doctor_id: ID of the doctor requesting deletion
        db: Database session
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    record = db.query(MedicalHistory).filter(MedicalHistory.id == record_id).first()
    
    if not record:
        return False, "Medical record not found"
    
    # Only the doctor who created the record can delete it
    if record.doctor_id != doctor_id:
        return False, "You can only delete your own diagnosis records"
    
    db.delete(record)
    db.commit()
    
    return True, "Diagnosis record deleted successfully"
