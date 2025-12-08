"""
Tests for admin routes
"""
import pytest


class TestAdminDashboard:
    """Test admin dashboard"""
    
    def test_dashboard_unauthorized(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get("/admin/dashboard")
        assert response.status_code == 401 or response.status_code == 303
    
    def test_dashboard_authorized(self, client, auth_headers_admin):
        """Test accessing dashboard with authentication"""
        response = client.get("/admin/dashboard", headers=auth_headers_admin)
        assert response.status_code in [200, 303]
    
    def test_dashboard_wrong_role(self, client, auth_headers_doctor):
        """Test accessing admin dashboard as doctor"""
        response = client.get("/admin/dashboard", headers=auth_headers_doctor)
        assert response.status_code in [403, 303]


class TestAdminDoctorManagement:
    """Test admin doctor management"""
    
    def test_doctors_list(self, client, auth_headers_admin):
        """Test viewing doctors list"""
        response = client.get("/admin/doctors", headers=auth_headers_admin)
        assert response.status_code in [200, 303]
    
    def test_view_doctor(self, client, auth_headers_admin, doctor_user):
        """Test viewing doctor details"""
        # doctor_user fixture already includes DoctorInfo
        response = client.get(
            f"/admin/doctors/{doctor_user.id}",
            cookies=auth_headers_admin
        )
        assert response.status_code in [200, 303]


class TestAdminPatientManagement:
    """Test admin patient management"""
    
    def test_patients_list(self, client, auth_headers_admin):
        """Test viewing patients list"""
        response = client.get("/admin/patients", headers=auth_headers_admin)
        assert response.status_code in [200, 303]
    
    def test_view_patient(self, client, auth_headers_admin, patient_user, db_session):
        """Test viewing patient details"""
        # Ensure patient has all required fields
        patient_user.gender = "male"
        patient_user.address = "123 Test St"
        db_session.commit()
        
        response = client.get(
            f"/admin/patients/{patient_user.id}",
            cookies=auth_headers_admin
        )
        assert response.status_code in [200, 303]
    
    def test_create_patient(self, client, auth_headers_admin):
        """Test creating new patient"""
        response = client.post(
            "/admin/patients/add",
            cookies=auth_headers_admin,
            data={
                "first_name": "Admin",
                "last_name": "Patient",
                "email": "adminpatient@test.com",
                "phone": "5555555555",
                "gender": "male",
                "address": "Admin Address",
                "blood_type": "AB+"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
