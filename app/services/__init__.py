# Services package
"""
Centralized services for the Blood Diagnosis application

Modules:
- auth_service: Authentication, JWT tokens, and password hashing
- ui_service: Flash messages and UI utilities
- patient_service: Patient management and doctor-patient relationships  
- ai_service: AI predictions for CBC analysis and blood images
- policy_service: Access control, permissions, and authorization policies
"""

from .auth_service import (
    verify_password,
    hash_password,
    create_access_token,
    verify_token,
    get_current_user,
    get_current_user_from_cookie,
    get_current_user_optional,
    require_role,
    require_authentication,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from .ui_service import (
    set_flash_message,
    add_message,
    get_flash_message
)

from .patient_service import (
    create_patient,
    get_patient_doctors,
    get_doctor_patients,
    link_patient_to_doctor,
    unlink_patient_from_doctor
)

from .ai_service import (
    CBCPredictionService,
    BloodImageAnalysisService,
    cbc_prediction_service,
    blood_image_service
)

from .policy_service import (
    check_account_active,
    require_active_account,
    check_patient_access,
    require_patient_access,
    can_upload_test,
    can_view_patient_data,
    can_add_diagnosis,
    can_modify_diagnosis,
    require_diagnosis_permission,
    can_manage_users,
    handle_policy_violation,
    check_role_permission,
    AccountDeactivatedException,
    PermissionDeniedException
)

__all__ = [
    # Auth
    "verify_password",
    "hash_password",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "get_current_user_from_cookie",
    "get_current_user_optional",
    "require_role",
    "require_authentication",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    # UI
    "set_flash_message",
    "add_message",
    "get_flash_message",
    # Patient
    "create_patient",
    "get_patient_doctors",
    "get_doctor_patients",
    "link_patient_to_doctor",
    "unlink_patient_from_doctor",
    # AI
    "CBCPredictionService",
    "BloodImageAnalysisService",
    "cbc_prediction_service",
    "blood_image_service",
    # Policy
    "check_account_active",
    "require_active_account",
    "check_patient_access",
    "require_patient_access",
    "can_upload_test",
    "can_view_patient_data",
    "can_add_diagnosis",
    "can_modify_diagnosis",
    "require_diagnosis_permission",
    "can_manage_users",
    "handle_policy_violation",
    "check_role_permission",
    "AccountDeactivatedException",
    "PermissionDeniedException"
]
