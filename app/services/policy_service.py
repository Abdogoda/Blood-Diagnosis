"""
Policy Service - Centralized access control and permission policies
Handles account activation, role-based restrictions, and other access policies
"""

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import User


class AccountDeactivatedException(Exception):
    """Exception raised when trying to access with a deactivated account"""
    def __init__(self, user_role: str):
        self.user_role = user_role
        super().__init__(f"Account is deactivated")


def check_account_active(user: User) -> bool:
    """
    Check if a user account is active
    Returns True if active, False if deactivated
    """
    return user.is_active == 1


def require_active_account(user: User, redirect_url: str = None):
    """
    Verify that a user's account is active
    Raises AccountDeactivatedException if deactivated
    
    Args:
        user: The user to check
        redirect_url: Optional URL to redirect to if deactivated
    
    Raises:
        AccountDeactivatedException: If account is not active
    """
    if not check_account_active(user):
        raise AccountDeactivatedException(user.role)


def can_upload_test(user: User) -> tuple[bool, str]:
    """
    Check if a user can upload tests
    
    Args:
        user: The user to check
        
    Returns:
        Tuple of (can_upload: bool, reason: str)
    """
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Check role permissions
    if user.role not in ["doctor", "patient", "admin"]:
        return False, "unauthorized"
    
    return True, ""


def can_view_patient_data(user: User, patient_id: int, db: Session) -> tuple[bool, str]:
    """
    Check if a user can view patient data
    
    Args:
        user: The user requesting access
        patient_id: The patient ID to access
        db: Database session
        
    Returns:
        Tuple of (can_view: bool, reason: str)
    """
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Admin can view all
    if user.role == "admin":
        return True, ""
    
    # Patient can view own data
    if user.role == "patient" and user.id == patient_id:
        return True, ""
    
    # Doctor can view if patient is linked
    if user.role == "doctor":
        from app.services.patient_service import is_patient_linked_to_doctor
        if is_patient_linked_to_doctor(patient_id, user.id, db):
            return True, ""
        return False, "not_linked"
    
    return False, "unauthorized"


def can_add_diagnosis(user: User, patient_id: int, db: Session) -> tuple[bool, str]:
    """
    Check if a user can add diagnosis for a patient
    
    Args:
        user: The user requesting access
        patient_id: The patient ID
        db: Database session
        
    Returns:
        Tuple of (can_add: bool, reason: str)
    """
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Only doctors and admins can add diagnosis
    if user.role not in ["doctor", "admin"]:
        return False, "unauthorized"
    
    # For doctors, check if patient is linked
    if user.role == "doctor":
        from app.services.patient_service import is_patient_linked_to_doctor
        if not is_patient_linked_to_doctor(patient_id, user.id, db):
            return False, "not_linked"
    
    return True, ""


def can_manage_users(user: User) -> tuple[bool, str]:
    """
    Check if a user can manage other users
    
    Args:
        user: The user to check
        
    Returns:
        Tuple of (can_manage: bool, reason: str)
    """
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Only admins can manage users
    if user.role != "admin":
        return False, "unauthorized"
    
    return True, ""


def get_deactivation_message(user_role: str) -> dict:
    """
    Get a formatted deactivation message for a user role
    
    Args:
        user_role: The role of the deactivated user
        
    Returns:
        Dictionary with title and message
    """
    messages = {
        "doctor": {
            "title": "Account Deactivated",
            "message": "Your doctor account has been deactivated by the administrator. You no longer have access to patient data, diagnosis tools, or test uploads.",
            "contact_subject": "Doctor Account Deactivation - Request for Information"
        },
        "patient": {
            "title": "Account Deactivated", 
            "message": "Your patient account has been deactivated by the administrator. You no longer have access to test uploads, medical history, or reports.",
            "contact_subject": "Patient Account Deactivation - Request for Information"
        },
        "admin": {
            "title": "Account Deactivated",
            "message": "Your administrator account has been deactivated. Please contact the system administrator.",
            "contact_subject": "Admin Account Deactivation - Request for Information"
        }
    }
    
    return messages.get(user_role, {
        "title": "Account Deactivated",
        "message": "Your account has been deactivated by the administrator.",
        "contact_subject": "Account Deactivation - Request for Information"
    })


def handle_policy_violation(request: Request, user: User, violation_type: str):
    """
    Handle policy violations with appropriate responses
    
    Args:
        request: FastAPI request object
        user: The user who violated the policy
        violation_type: Type of violation (deactivated, unauthorized, not_linked)
        
    Returns:
        RedirectResponse with flash message
    """
    from app.services import set_flash_message
    
    if violation_type == "deactivated":
        # Simply redirect to deactivated page - no session needed
        return RedirectResponse(url="/account-deactivated", status_code=303)
    
    elif violation_type == "unauthorized":
        response = RedirectResponse(url=f"/{user.role}/dashboard", status_code=303)
        set_flash_message(response, "error", "You don't have permission to access this resource.")
        return response
    
    elif violation_type == "not_linked":
        response = RedirectResponse(url=f"/{user.role}/dashboard", status_code=303)
        set_flash_message(response, "error", "You don't have access to this patient's data.")
        return response
    
    else:
        response = RedirectResponse(url="/", status_code=303)
        set_flash_message(response, "error", "Access denied.")
        return response
