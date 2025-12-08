"""
User Interface Service
Handles flash messages and UI-related utilities
"""
from typing import Optional
from fastapi import Request, Response
import json
from urllib.parse import quote, unquote


def set_flash_message(response: Response, message_type: str, message: str):
    flash_data = json.dumps({"type": message_type, "message": message})
    encoded_data = quote(flash_data)
    response.set_cookie(
        key="flash_message",
        value=encoded_data,
        max_age=60,
        httponly=False,
        samesite="lax",
        path="/"
    )


def add_message(context: dict, message_type: str, message: str):
    if "messages" not in context:
        context["messages"] = []
    
    context["messages"].append({
        "type": message_type,
        "message": message
    })


def get_flash_message(request: Request) -> Optional[dict]:
    flash_cookie = request.cookies.get("flash_message")
    
    if not flash_cookie:
        return None
    
    try:
        decoded_data = unquote(flash_cookie)
        flash_data = json.loads(decoded_data)
        return flash_data
    except (json.JSONDecodeError, ValueError):
        return None
