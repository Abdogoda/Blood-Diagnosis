"""
Tests for authentication routes
"""
import pytest


class TestLoginRoutes:
    """Test login functionality"""
    
    def test_login_page_get(self, client):
        """Test GET /auth/login"""
        response = client.get("/auth/login")
        assert response.status_code == 200
    
    def test_login_success_admin(self, client, admin_user):
        """Test successful admin login"""
        response = client.post(
            "/auth/login",
            data={"email": "admin@test.com", "password": "admin123"},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/admin/dashboard"
        assert "access_token" in response.cookies
    
    def test_login_success_doctor(self, client, doctor_user):
        """Test successful doctor login"""
        response = client.post(
            "/auth/login",
            data={"email": "doctor@test.com", "password": "doctor123"},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/doctor/dashboard"
    
    def test_login_success_patient(self, client, patient_user):
        """Test successful patient login"""
        response = client.post(
            "/auth/login",
            data={"email": "patient@test.com", "password": "patient123"},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/patient/dashboard"
    
    def test_login_invalid_credentials(self, client, admin_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            data={"email": "admin@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 400
        assert b"Incorrect email or password" in response.content
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            data={"email": "nonexistent@test.com", "password": "password"}
        )
        assert response.status_code == 400


class TestRegisterRoutes:
    """Test registration functionality"""
    
    def test_register_page_get(self, client):
        """Test GET /auth/register"""
        response = client.get("/auth/register")
        assert response.status_code == 200
    
    def test_register_patient_success(self, client):
        """Test successful patient registration"""
        response = client.post(
            "/auth/register",
            data={
                "email": "newpatient@test.com",
                "password": "password123",
                "confirm-password": "password123",
                "fname": "New",
                "lname": "Patient",
                "role": "patient",
                "phone": "1112223333",
                "gender": "male",
                "blood_type": "A+",
                "address": "123 Test St"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
    
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        response = client.post(
            "/auth/register",
            data={
                "email": "test@test.com",
                "password": "password123",
                "confirm-password": "different123",
                "fname": "Test",
                "lname": "User",
                "role": "patient",
                "phone": "1112223333",
                "gender": "male",
                "blood_type": "A+",
                "address": "123 Test St"
            }
        )
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client, patient_user):
        """Test registration with existing email"""
        response = client.post(
            "/auth/register",
            data={
                "email": "patient@test.com",  # Already exists
                "password": "password123",
                "confirm-password": "password123",
                "fname": "Test",
                "lname": "User",
                "role": "patient",
                "phone": "1112223333",
                "gender": "male",
                "blood_type": "A+",
                "address": "123 Test St"
            }
        )
        assert response.status_code == 400
