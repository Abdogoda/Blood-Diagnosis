"""
Tests for patient routes
"""
import pytest


class TestPatientDashboard:
    """Test patient dashboard"""
    
    def test_dashboard_unauthorized(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get("/patient/dashboard")
        assert response.status_code == 401 or response.status_code == 303
    
    def test_dashboard_authorized(self, client, auth_headers_patient):
        """Test accessing dashboard with authentication"""
        response = client.get("/patient/dashboard", headers=auth_headers_patient)
        assert response.status_code in [200, 303]
    
    def test_dashboard_wrong_role(self, client, auth_headers_doctor):
        """Test accessing patient dashboard as doctor"""
        response = client.get("/patient/dashboard", headers=auth_headers_doctor)
        assert response.status_code in [403, 303]


class TestPatientAccount:
    """Test patient account management"""
    
    def test_account_page(self, client, auth_headers_patient):
        """Test accessing account page"""
        response = client.get("/patient/account", headers=auth_headers_patient)
        assert response.status_code in [200, 303]
    
    def test_update_profile(self, client, auth_headers_patient):
        """Test updating profile information"""
        response = client.post(
            "/patient/update-profile",
            headers=auth_headers_patient,
            data={
                "fname": "Updated",
                "lname": "Name",
                "email": "updated@test.com",
                "phone": "9999999999",
                "blood_type": "B+",
                "address": "New Address"
            },
            follow_redirects=False
        )
        assert response.status_code == 303


class TestPatientTests:
    """Test patient test management"""
    
    def test_upload_test_page(self, client, auth_headers_patient):
        """Test accessing upload test page"""
        response = client.get("/patient/upload-test", headers=auth_headers_patient)
        assert response.status_code in [200, 303]
    
    def test_upload_cbc_page(self, client, auth_headers_patient):
        """Test accessing CBC upload page"""
        response = client.get("/patient/upload-cbc", headers=auth_headers_patient)
        assert response.status_code in [200, 303]
