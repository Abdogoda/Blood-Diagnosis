"""
Policy Service - Centralized access control and permission policies
Handles account activation, role-based restrictions, and other access policies
"""

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import User

# Initialize templates
templates = Jinja2Templates(directory="app/templates")


class AccountDeactivatedException(Exception):
    """Exception raised when trying to access with a deactivated account"""
    def __init__(self, user_role: str):
        self.user_role = user_role
        super().__init__(f"Account is deactivated")


class PermissionDeniedException(Exception):
    """Exception raised when user doesn't have permission"""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Permission denied: {reason}")


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


def check_patient_access(
    current_user: User,
    patient: User,
    db: Session
) -> tuple[bool, str]:
    """
    Check if current user has access to a patient's data
    
    Args:
        current_user: The user requesting access
        patient: The patient whose data is being accessed
        db: Database session
        
    Returns:
        Tuple of (has_access: bool, reason: str)
        reason can be: "deactivated_user", "deactivated_patient", "not_linked", "unauthorized", ""
    """
    # Check if current user's account is active
    if not check_account_active(current_user):
        return False, "deactivated_user"
    
    # Check if patient's account is active
    if not check_account_active(patient):
        return False, "deactivated_patient"
    
    # Admin has access to all patients
    if current_user.role == "admin":
        return True, ""
    
    # Patient can access their own data
    if current_user.role == "patient" and current_user.id == patient.id:
        return True, ""
    
    # Doctor must have patient linked
    if current_user.role == "doctor":
        if patient in current_user.patients:
            return True, ""
        return False, "not_linked"
    
    return False, "unauthorized"


def require_patient_access(
    request: Request,
    current_user: User,
    patient: User,
    db: Session
):
    """
    Check patient access and return error response if denied
    Returns None if access is granted, otherwise returns Response
    
    Args:
        request: FastAPI request
        current_user: The user requesting access
        patient: The patient being accessed
        db: Database session
        
    Returns:
        None if access granted, otherwise RedirectResponse or TemplateResponse
    """
    has_access, reason = check_patient_access(current_user, patient, db)
    
    if not has_access:
        if reason == "deactivated_user":
            return RedirectResponse(url="/account-deactivated", status_code=303)
        elif reason == "deactivated_patient":
            return handle_policy_violation(request, current_user, "deactivated_patient")
        elif reason == "not_linked":
            return templates.TemplateResponse("errors/403.html", {
                "request": request,
                "current_user": current_user,
                "message": "You don't have access to this patient"
            }, status_code=403)
        else:
            return templates.TemplateResponse("errors/403.html", {
                "request": request,
                "current_user": current_user,
                "message": "You don't have permission to access this resource"
            }, status_code=403)
    
    return None


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
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    if not patient:
        return False, "patient_not_found"
    
    # Check patient's account status
    if not check_account_active(patient):
        return False, "deactivated_patient"
    
    # Admin can add diagnosis for any patient
    if user.role == "admin":
        return True, ""
    
    # For doctors, check if patient is linked
    if user.role == "doctor":
        if patient not in user.patients:
            return False, "not_linked"
    
    return True, ""


def can_modify_diagnosis(user: User, record_id: int, db: Session) -> tuple[bool, str]:
    """
    Check if a user can modify (update/delete) a diagnosis record
    
    Args:
        user: The user requesting access
        record_id: The medical history record ID
        db: Database session
        
    Returns:
        Tuple of (can_modify: bool, reason: str)
    """
    from app.database import MedicalHistory
    
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Only doctors and admins can modify diagnosis
    if user.role not in ["doctor", "admin"]:
        return False, "unauthorized"
    
    # Get the record
    record = db.query(MedicalHistory).filter(MedicalHistory.id == record_id).first()
    if not record:
        return False, "record_not_found"
    
    # Admin can modify any record
    if user.role == "admin":
        return True, ""
    
    # Doctors can only modify their own records
    if user.role == "doctor":
        if record.doctor_id != user.id:
            return False, "not_owner"
    
    return True, ""


def require_diagnosis_permission(
    request: Request,
    user: User,
    patient_id: int,
    db: Session
):
    can_add, reason = can_add_diagnosis(user, patient_id, db)
    
    if not can_add:
        if reason == "deactivated":
            return RedirectResponse(url="/account-deactivated", status_code=303)
        elif reason == "deactivated_patient":
            from app.services import set_flash_message
            response = RedirectResponse(url=f"/{user.role}/patients", status_code=303)
            set_flash_message(response, "error", "This patient's account is deactivated.")
            return response
        elif reason == "patient_not_found":
            from app.services import set_flash_message
            response = RedirectResponse(url=f"/{user.role}/patients", status_code=303)
            set_flash_message(response, "error", "Patient not found.")
            return response
        elif reason == "not_linked":
            return templates.TemplateResponse("errors/403.html", {
                "request": request,
                "current_user": user,
                "message": "You don't have access to add diagnosis for this patient"
            }, status_code=403)
        else:
            return templates.TemplateResponse("errors/403.html", {
                "request": request,
                "current_user": user,
                "message": "You don't have permission to add diagnosis"
            }, status_code=403)
    
    return None


def can_manage_users(user: User) -> tuple[bool, str]:
    # Check if account is active
    if not check_account_active(user):
        return False, "deactivated"
    
    # Only admins can manage users
    if user.role != "admin":
        return False, "unauthorized"
    
    return True, ""


def get_deactivation_message(user_role: str) -> dict:
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
    from app.services import set_flash_message
    
    if violation_type == "deactivated":
        # Simply redirect to deactivated page - no session needed
        return RedirectResponse(url="/account-deactivated", status_code=303)
    
    elif violation_type == "deactivated_patient":
        response = RedirectResponse(url=f"/{user.role}/patients", status_code=303)
        set_flash_message(response, "error", "This patient's account is deactivated.")
        return response
    
    elif violation_type == "unauthorized":
        response = RedirectResponse(url=f"/{user.role}/dashboard", status_code=303)
        set_flash_message(response, "error", "You don't have permission to access this resource.")
        return response
    
    elif violation_type == "not_linked":
        return templates.TemplateResponse("errors/403.html", {
            "request": request,
            "current_user": user,
            "message": "You don't have access to this patient"
        }, status_code=403)
    
    else:
        response = RedirectResponse(url="/", status_code=303)
        set_flash_message(response, "error", "Access denied.")
        return response


def check_role_permission(user: User, allowed_roles: list[str]) -> tuple[bool, str]:
    if not check_account_active(user):
        return False, "deactivated"
    
    if user.role not in allowed_roles:
        return False, "unauthorized"
    
    return True, ""
