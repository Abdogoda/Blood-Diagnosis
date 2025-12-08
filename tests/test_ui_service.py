"""
Tests for UI service
"""
import pytest
import json
from urllib.parse import quote
from fastapi.responses import RedirectResponse
from app.services import set_flash_message, get_flash_message, add_message


class TestFlashMessages:
    """Test flash message functionality"""
    
    def test_set_flash_message_success(self):
        """Test setting success flash message"""
        response = RedirectResponse(url="/test", status_code=303)
        set_flash_message(response, "success", "Test success message")
        
        # Function should execute without error
        assert response is not None
    
    def test_set_flash_message_error(self):
        """Test setting error flash message"""
        response = RedirectResponse(url="/test", status_code=303)
        set_flash_message(response, "error", "Test error message")
        
        assert response is not None
    
    def test_set_flash_message_warning(self):
        """Test setting warning flash message"""
        response = RedirectResponse(url="/test", status_code=303)
        set_flash_message(response, "warning", "Test warning message")
        
        assert response is not None
    
    def test_add_message(self):
        """Test adding messages to context"""
        context = {}
        
        add_message(context, "success", "First message")
        add_message(context, "error", "Second message")
        
        assert "messages" in context
        assert len(context["messages"]) == 2
        assert context["messages"][0]["type"] == "success"
        assert context["messages"][0]["message"] == "First message"
        assert context["messages"][1]["type"] == "error"
        assert context["messages"][1]["message"] == "Second message"
    
    def test_get_flash_message_none(self):
        """Test getting flash message when none exists"""
        class MockRequest:
            cookies = {}
        
        request = MockRequest()
        result = get_flash_message(request)
        
        assert result is None
    
    def test_get_flash_message_with_data(self):
        """Test getting flash message with valid data"""
        flash_data = json.dumps({"type": "success", "message": "Test message"})
        encoded_data = quote(flash_data)
        
        class MockRequest:
            cookies = {"flash_message": encoded_data}
        
        request = MockRequest()
        result = get_flash_message(request)
        
        assert result is not None
        assert result["type"] == "success"
        assert result["message"] == "Test message"

