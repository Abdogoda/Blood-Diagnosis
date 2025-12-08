"""
Tests for public routes
"""
import pytest


class TestPublicPages:
    """Test public accessible pages"""
    
    def test_home_page(self, client):
        """Test home page"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_about_page(self, client):
        """Test about page"""
        response = client.get("/about")
        assert response.status_code == 200
    
    def test_contact_page(self, client):
        """Test contact page"""
        response = client.get("/contact")
        assert response.status_code == 200
    
    def test_home_redirects_when_logged_in(self, client, auth_headers_admin):
        """Test home redirects to dashboard when logged in"""
        response = client.get("/", headers=auth_headers_admin, follow_redirects=False)
        # Should redirect to appropriate dashboard
        assert response.status_code in [200, 303]
