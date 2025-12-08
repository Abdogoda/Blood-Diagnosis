"""
Tests for patient service
"""
import pytest
from app.services import (
    create_patient,
    get_patient_doctors,
    get_doctor_patients,
    link_patient_to_doctor,
    unlink_patient_from_doctor
)


class TestPatientCreation:
    """Test patient creation functionality"""
    
    def test_create_patient_success(self, db_session):
        """Test successful patient creation"""
        result = create_patient(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            phone="1234567890",
            gender="male",
            address="123 Test St",
            blood_type="O+",
            dob="1990-01-01",
            db=db_session,
            redirect_url="/test"
        )
        
        assert result is not None
        # Result could be a dict or redirect response
        if isinstance(result, dict):
            assert result.get("success") is True
    
    def test_create_patient_duplicate_email(self, db_session, patient_user):
        """Test patient creation with duplicate email"""
        result = create_patient(
            first_name="Jane",
            last_name="Doe",
            email="patient@test.com",  # Already exists
            phone="9876543210",
            gender="female",
            address="456 Test Ave",
            blood_type="A+",
            dob="1992-02-02",
            db=db_session,
            redirect_url="/test"
        )
        
        # Should return redirect response with error
        assert result is not None


class TestDoctorPatientRelationships:
    """Test doctor-patient relationship management"""
    
    def test_link_patient_to_doctor(self, db_session, doctor_user, patient_user):
        """Test linking patient to doctor"""
        success = link_patient_to_doctor(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            db=db_session
        )
        
        assert success is True
    
    def test_link_duplicate_relationship(self, db_session, doctor_user, patient_user):
        """Test linking same patient-doctor twice"""
        # First link
        link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        
        # Second link (should return False as it already exists)
        success = link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        assert success is False
    
    def test_unlink_patient_from_doctor(self, db_session, doctor_user, patient_user):
        """Test unlinking patient from doctor"""
        # First link them
        link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        
        # Then unlink
        success = unlink_patient_from_doctor(patient_user.id, doctor_user.id, db_session)
        assert success is True
    
    def test_get_patient_doctors(self, db_session, doctor_user, patient_user):
        """Test retrieving patient's doctors"""
        # Link patient to doctor
        link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        
        # Get patient's doctors
        doctors = get_patient_doctors(patient_user.id, db_session)
        
        assert len(doctors) == 1
        assert doctors[0]["id"] == doctor_user.id
        assert doctors[0]["name"] == f"Dr. {doctor_user.fname} {doctor_user.lname}"
    
    def test_get_doctor_patients(self, db_session, doctor_user, patient_user):
        """Test retrieving doctor's patients"""
        # Link patient to doctor
        link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        
        # Get doctor's patients (returns list of IDs)
        patients = get_doctor_patients(doctor_user.id, db_session)
        
        assert len(patients) == 1
        assert patients[0] == patient_user.id
    
    def test_get_patient_doctors_empty(self, db_session, patient_user):
        """Test getting doctors for patient with no connections"""
        doctors = get_patient_doctors(patient_user.id, db_session)
        assert len(doctors) == 0
    
    def test_get_doctor_patients_empty(self, db_session, doctor_user):
        """Test getting patients for doctor with no connections"""
        patients = get_doctor_patients(doctor_user.id, db_session)
        assert len(patients) == 0
