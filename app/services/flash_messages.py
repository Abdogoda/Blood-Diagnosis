"""
Utility functions for flash messages.
"""
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
import json
from urllib.parse import quote


def set_flash_message(response: Response, message_type: str, message: str):
    """
    Set a flash message as a cookie in the response.
    
    Args:
        response: Response object to set cookie on
        message_type: Type of message (error, success, warning, info)
        message: Message text to display
    """
    flash_data = json.dumps({"type": message_type, "message": message})
    # URL encode the JSON string to handle special characters
    encoded_data = quote(flash_data)
    response.set_cookie(
        key="flash_message",
        value=encoded_data,
        max_age=60,  # Message expires after 60 seconds
        httponly=False,  # Allow JavaScript to read for display
        samesite="lax",
        path="/"  # Make cookie available across all paths
    )


def add_message(context: dict, message_type: str, message: str):
    """
    Add a flash message to the template context.
    
    Args:
        context: Template context dictionary
        message_type: Type of message (error, success, warning, info)
        message: Message text to display
    """
    context[message_type] = message


def render_with_message(
    templates: Jinja2Templates,
    template_name: str,
    request: Request,
    message_type: str,
    message: str,
    status_code: int = 200,
    **extra_context
):
    """
    Render a template with a flash message.
    
    Args:
        templates: Jinja2Templates instance
        template_name: Name of the template to render
        request: HTTP request object
        message_type: Type of message (error, success, warning, info)
        message: Message text to display
        status_code: HTTP status code
        **extra_context: Additional context variables
        
    Returns:
        TemplateResponse with message
    """
    context = {
        "request": request,
        message_type: message,
        **extra_context
    }
    return templates.TemplateResponse(template_name, context, status_code=status_code)
