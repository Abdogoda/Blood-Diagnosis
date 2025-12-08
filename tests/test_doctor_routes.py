"""
Tests for doctor routes
"""
import pytest


class TestDoctorDashboard:
    """Test doctor dashboard"""
    
    def test_dashboard_unauthorized(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get("/doctor/dashboard")
        assert response.status_code == 401 or response.status_code == 303
    
    def test_dashboard_authorized(self, client, auth_headers_doctor):
        """Test accessing dashboard with authentication"""
        response = client.get("/doctor/dashboard", headers=auth_headers_doctor)
        # May redirect or show page depending on implementation
        assert response.status_code in [200, 303]
    
    def test_dashboard_wrong_role(self, client, auth_headers_patient):
        """Test accessing doctor dashboard as patient"""
        response = client.get("/doctor/dashboard", headers=auth_headers_patient)
        # Should be forbidden or redirect
        assert response.status_code in [403, 303]


class TestDoctorPatients:
    """Test doctor patient management"""
    
    def test_patients_list(self, client, auth_headers_doctor):
        """Test viewing patients list"""
        response = client.get("/doctor/patients", headers=auth_headers_doctor)
        assert response.status_code in [200, 303]
    
    def test_add_patient_page(self, client, auth_headers_doctor):
        """Test add patient page"""
        response = client.get("/doctor/add-patient", headers=auth_headers_doctor)
        assert response.status_code in [200, 303]
    
    def test_create_patient(self, client, auth_headers_doctor, db_session):
        """Test creating a new patient"""
        response = client.post(
            "/doctor/patient/add",
            cookies=auth_headers_doctor,
            data={
                "first_name": "Test",
                "last_name": "Patient",
                "email": "testpatient@test.com",
                "phone": "1234567890",
                "gender": "male",
                "address": "Test Address",
                "blood_type": "O+"
            },
            follow_redirects=False
        )
        # Should redirect after success
        assert response.status_code == 303


class TestDoctorPatientRelationships:
    """Test linking/unlinking patients"""
    
    def test_link_patient(self, client, auth_headers_doctor, doctor_user, patient_user, db_session):
        """Test linking patient to doctor"""
        response = client.post(
            f"/doctor/patient/{patient_user.id}/link",
            headers=auth_headers_doctor,
            follow_redirects=False
        )
        assert response.status_code == 303
    
    def test_unlink_patient(self, client, auth_headers_doctor, doctor_user, patient_user, db_session):
        """Test unlinking patient from doctor"""
        # First link
        from app.services import link_patient_to_doctor
        link_patient_to_doctor(patient_user.id, doctor_user.id, db_session)
        
        # Then unlink
        response = client.post(
            f"/doctor/patient/{patient_user.id}/unlink",
            headers=auth_headers_doctor,
            follow_redirects=False
        )
        assert response.status_code == 303
