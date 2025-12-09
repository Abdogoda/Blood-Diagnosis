"""
Tests for medical history service
"""
import pytest
from datetime import datetime
from app.services.medical_history_service import (
    create_diagnosis,
    get_patient_medical_history,
    update_diagnosis,
    delete_diagnosis
)
from app.database import MedicalHistory


class TestCreateDiagnosis:
    """Test creating diagnosis records"""
    
    def test_create_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test successful diagnosis creation"""
        # Link doctor to patient
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            treatment="Iron supplements",
            notes="Mild case",
            db=db_session
        )
        
        assert success is True
        assert "successfully" in message.lower()
        assert record is not None
        assert record.patient_id == patient_user.id
        assert record.doctor_id == doctor_user.id
        assert record.medical_condition == "Anemia"
    
    def test_create_diagnosis_doctor_not_found(self, db_session, patient_user):
        """Test diagnosis creation with non-existent doctor"""
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=99999,
            medical_condition="Anemia",
            db=db_session
        )
        
        assert success is False
        assert "not found" in message.lower()
        assert record is None
    
    def test_create_diagnosis_patient_not_found(self, db_session, doctor_user):
        """Test diagnosis creation with non-existent patient"""
        success, message, record = create_diagnosis(
            patient_id=99999,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        assert success is False
        assert record is None
    
    def test_create_diagnosis_not_linked(self, db_session, doctor_user, patient_user):
        """Test diagnosis creation when doctor-patient not linked"""
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        assert success is False
        assert "access" in message.lower() or "linked" in message.lower()
        assert record is None
    
    def test_create_diagnosis_deactivated_doctor(self, db_session, doctor_user, patient_user):
        """Test diagnosis creation with deactivated doctor"""
        doctor_user.is_active = 0
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        assert success is False
        assert "deactivated" in message.lower()
        assert record is None
    
    def test_create_diagnosis_deactivated_patient(self, db_session, doctor_user, patient_user):
        """Test diagnosis creation with deactivated patient"""
        doctor_user.patients.append(patient_user)
        patient_user.is_active = 0
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        assert success is False
        assert "deactivated" in message.lower()
        assert record is None
    
    def test_create_diagnosis_with_all_fields(self, db_session, doctor_user, patient_user):
        """Test diagnosis creation with all optional fields"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Iron Deficiency Anemia",
            treatment="Ferrous sulfate 325mg daily",
            notes="Patient shows signs of fatigue and weakness",
            db=db_session
        )
        
        assert success is True
        assert record.treatment == "Ferrous sulfate 325mg daily"
        assert record.notes == "Patient shows signs of fatigue and weakness"


class TestGetPatientMedicalHistory:
    """Test retrieving patient medical history"""
    
    def test_get_medical_history_empty(self, db_session, patient_user):
        """Test getting medical history with no records"""
        history = get_patient_medical_history(patient_user.id, db_session)
        
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_get_medical_history_single_record(self, db_session, doctor_user, patient_user):
        """Test getting medical history with one record"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            treatment="Iron supplements",
            db=db_session
        )
        
        history = get_patient_medical_history(patient_user.id, db_session)
        
        assert len(history) == 1
        assert history[0]['condition'] == "Anemia"
        assert history[0]['treatment'] == "Iron supplements"
        assert 'doctor_name' in history[0]
        assert 'date' in history[0]
    
    def test_get_medical_history_multiple_records(self, db_session, doctor_user, patient_user):
        """Test getting medical history with multiple records"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        # Create multiple diagnosis records
        conditions = ["Anemia", "Leukopenia", "Thrombocytopenia"]
        for condition in conditions:
            create_diagnosis(
                patient_id=patient_user.id,
                doctor_id=doctor_user.id,
                medical_condition=condition,
                db=db_session
            )
        
        history = get_patient_medical_history(patient_user.id, db_session)
        
        assert len(history) == 3
        # Should be ordered by most recent first
        assert all('condition' in record for record in history)
    
    def test_get_medical_history_with_deleted_doctor(self, db_session, doctor_user, patient_user):
        """Test getting medical history after doctor is deleted"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        # Create diagnosis
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        # Manually set doctor_id to None (simulating deletion)
        record.doctor_id = None
        db_session.commit()
        
        history = get_patient_medical_history(patient_user.id, db_session)
        
        assert len(history) == 1
        assert history[0]['doctor_name'] == "Unknown"


class TestUpdateDiagnosis:
    """Test updating diagnosis records"""
    
    def test_update_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test successful diagnosis update"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            treatment="Iron supplements",
            db=db_session
        )
        
        success, message = update_diagnosis(
            record_id=record.id,
            doctor_id=doctor_user.id,
            medical_condition="Iron Deficiency Anemia",
            treatment="Increased iron dosage",
            notes="Patient improving",
            db=db_session
        )
        
        assert success is True
        assert "successfully" in message.lower() or "updated" in message.lower()
        
        # Verify update
        updated_record = db_session.query(MedicalHistory).filter(
            MedicalHistory.id == record.id
        ).first()
        assert updated_record.medical_condition == "Iron Deficiency Anemia"
        assert updated_record.treatment == "Increased iron dosage"
        assert updated_record.notes == "Patient improving"
    
    def test_update_diagnosis_not_owner(self, db_session, doctor_user, patient_user):
        """Test updating diagnosis by different doctor"""
        from app.services import hash_password
        from app.database import User, DoctorInfo
        
        # Create another doctor
        doctor2 = User(
            username="doctor2",
            email="doctor2@test.com",
            password=hash_password("doctor123"),
            fname="Jane",
            lname="Smith",
            role="doctor",
            is_active=1
        )
        db_session.add(doctor2)
        db_session.commit()
        
        doctor_info = DoctorInfo(
            user_id=doctor2.id,
            license_number="LIC456",
            specialization="Cardiology"
        )
        db_session.add(doctor_info)
        db_session.commit()
        
        # Link first doctor to patient
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        # Create diagnosis by first doctor
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        # Try to update by second doctor
        success, message = update_diagnosis(
            record_id=record.id,
            doctor_id=doctor2.id,
            medical_condition="Different diagnosis",
            db=db_session
        )
        
        assert success is False
        assert "own" in message.lower() or "owner" in message.lower()
    
    def test_update_diagnosis_record_not_found(self, db_session, doctor_user):
        """Test updating non-existent diagnosis"""
        success, message = update_diagnosis(
            record_id=99999,
            doctor_id=doctor_user.id,
            medical_condition="Something",
            db=db_session
        )
        
        assert success is False
        assert "not found" in message.lower()
    
    def test_update_diagnosis_deactivated_doctor(self, db_session, doctor_user, patient_user):
        """Test updating diagnosis with deactivated doctor"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        # Deactivate doctor
        doctor_user.is_active = 0
        db_session.commit()
        
        success, message = update_diagnosis(
            record_id=record.id,
            doctor_id=doctor_user.id,
            medical_condition="Updated",
            db=db_session
        )
        
        assert success is False
        assert "deactivated" in message.lower()
    
    def test_update_diagnosis_partial_update(self, db_session, doctor_user, patient_user):
        """Test partial update of diagnosis"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            treatment="Iron supplements",
            notes="Initial notes",
            db=db_session
        )
        
        # Update only notes
        success, message = update_diagnosis(
            record_id=record.id,
            doctor_id=doctor_user.id,
            notes="Updated notes only",
            db=db_session
        )
        
        assert success is True
        
        # Verify only notes changed
        updated_record = db_session.query(MedicalHistory).filter(
            MedicalHistory.id == record.id
        ).first()
        assert updated_record.notes == "Updated notes only"
        assert updated_record.medical_condition == "Anemia"
        assert updated_record.treatment == "Iron supplements"


class TestDeleteDiagnosis:
    """Test deleting diagnosis records"""
    
    def test_delete_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test successful diagnosis deletion"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        success, message = delete_diagnosis(
            record_id=record.id,
            doctor_id=doctor_user.id,
            db=db_session
        )
        
        assert success is True
        
        # Verify deletion
        deleted_record = db_session.query(MedicalHistory).filter(
            MedicalHistory.id == record.id
        ).first()
        assert deleted_record is None
    
    def test_delete_diagnosis_not_owner(self, db_session, doctor_user, patient_user):
        """Test deleting diagnosis by different doctor"""
        from app.services import hash_password
        from app.database import User, DoctorInfo
        
        # Create another doctor
        doctor2 = User(
            username="doctor2",
            email="doctor2@test.com",
            password=hash_password("doctor123"),
            fname="Jane",
            lname="Smith",
            role="doctor",
            is_active=1
        )
        db_session.add(doctor2)
        db_session.commit()
        
        doctor_info = DoctorInfo(
            user_id=doctor2.id,
            license_number="LIC456",
            specialization="Cardiology"
        )
        db_session.add(doctor_info)
        db_session.commit()
        
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        success, message, record = create_diagnosis(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Anemia",
            db=db_session
        )
        
        success, message = delete_diagnosis(
            record_id=record.id,
            doctor_id=doctor2.id,
            db=db_session
        )
        
        assert success is False
    
    def test_delete_diagnosis_not_found(self, db_session, doctor_user):
        """Test deleting non-existent diagnosis"""
        success, message = delete_diagnosis(
            record_id=99999,
            doctor_id=doctor_user.id,
            db=db_session
        )
        
        assert success is False
        assert "not found" in message.lower()
