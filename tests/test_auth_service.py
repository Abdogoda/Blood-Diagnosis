"""
Tests for authentication service
"""
import pytest
from datetime import timedelta
from app.services import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_long_password(self):
        """Test hashing of long password (>72 bytes)"""
        password = "a" * 100
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_token_with_expiration(self):
        """Test token creation with custom expiration"""
        data = {"sub": "testuser", "role": "doctor"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        data = {"sub": "testuser", "role": "patient"}
        token = create_access_token(data)
        
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.username == "testuser"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        token_data = verify_token(invalid_token)
        assert token_data is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        data = {"sub": "testuser", "role": "admin"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        token_data = verify_token(token)
        assert token_data is None
