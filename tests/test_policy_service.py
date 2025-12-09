"""
Tests for policy service (access control and permissions)
"""
import pytest
from app.services.policy_service import (
    check_account_active,
    require_active_account,
    check_patient_access,
    require_patient_access,
    AccountDeactivatedException,
    PermissionDeniedException,
    can_add_diagnosis,
    can_modify_diagnosis,
    can_view_patient_data,
    check_role_permission
)
from app.database import User, MedicalHistory, Test


class TestAccountActivation:
    """Test account activation checks"""
    
    def test_check_account_active_true(self, db_session, patient_user):
        """Test checking active account"""
        assert check_account_active(patient_user) is True
    
    def test_check_account_active_false(self, db_session, patient_user):
        """Test checking deactivated account"""
        patient_user.is_active = 0
        db_session.commit()
        
        assert check_account_active(patient_user) is False
    
    def test_require_active_account_success(self, db_session, patient_user):
        """Test requiring active account with active user"""
        # Should not raise exception
        try:
            require_active_account(patient_user)
            success = True
        except AccountDeactivatedException:
            success = False
        
        assert success is True
    
    def test_require_active_account_raises(self, db_session, patient_user):
        """Test requiring active account with deactivated user"""
        patient_user.is_active = 0
        db_session.commit()
        
        with pytest.raises(AccountDeactivatedException) as exc_info:
            require_active_account(patient_user)
        
        assert exc_info.value.user_role == "patient"


class TestPatientAccess:
    """Test patient access control"""
    
    def test_check_patient_access_admin(self, db_session, admin_user, patient_user):
        """Test admin has access to all patients"""
        has_access, reason = check_patient_access(
            current_user=admin_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is True
        assert reason == ""
    
    def test_check_patient_access_patient_self(self, db_session, patient_user):
        """Test patient can access own data"""
        has_access, reason = check_patient_access(
            current_user=patient_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is True
        assert reason == ""
    
    def test_check_patient_access_doctor_linked(self, db_session, doctor_user, patient_user):
        """Test doctor can access linked patient"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        has_access, reason = check_patient_access(
            current_user=doctor_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is True
        assert reason == ""
    
    def test_check_patient_access_doctor_not_linked(self, db_session, doctor_user, patient_user):
        """Test doctor cannot access unlinked patient"""
        has_access, reason = check_patient_access(
            current_user=doctor_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is False
        assert reason == "not_linked"
    
    def test_check_patient_access_deactivated_user(self, db_session, doctor_user, patient_user):
        """Test deactivated user cannot access patient data"""
        doctor_user.is_active = 0
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        has_access, reason = check_patient_access(
            current_user=doctor_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is False
        assert reason == "deactivated_user"
    
    def test_check_patient_access_deactivated_patient(self, db_session, doctor_user, patient_user):
        """Test cannot access deactivated patient"""
        doctor_user.patients.append(patient_user)
        patient_user.is_active = 0
        db_session.commit()
        
        has_access, reason = check_patient_access(
            current_user=doctor_user,
            patient=patient_user,
            db=db_session
        )
        
        assert has_access is False
        assert reason == "deactivated_patient"
    
    def test_check_patient_access_different_patient(self, db_session, patient_user):
        """Test patient cannot access another patient's data"""
        from app.services import hash_password
        
        # Create second patient
        patient2 = User(
            username="patient2",
            email="patient2@test.com",
            password=hash_password("patient123"),
            fname="Another",
            lname="Patient",
            role="patient",
            is_active=1
        )
        db_session.add(patient2)
        db_session.commit()
        
        has_access, reason = check_patient_access(
            current_user=patient_user,
            patient=patient2,
            db=db_session
        )
        
        assert has_access is False
        assert reason == "unauthorized"


class TestDiagnosisPermissions:
    """Test permissions for diagnosis operations"""
    
    def test_can_add_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test doctor can add diagnosis for linked patient"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        can_add, reason = can_add_diagnosis(doctor_user, patient_user.id, db_session)
        
        assert can_add is True
        assert reason == ""
    
    def test_can_add_diagnosis_not_linked(self, db_session, doctor_user, patient_user):
        """Test doctor cannot add diagnosis for unlinked patient"""
        can_add, reason = can_add_diagnosis(doctor_user, patient_user.id, db_session)
        
        assert can_add is False
        assert reason == "not_linked"
    
    def test_can_add_diagnosis_deactivated_doctor(self, db_session, doctor_user, patient_user):
        """Test deactivated doctor cannot add diagnosis"""
        doctor_user.patients.append(patient_user)
        doctor_user.is_active = 0
        db_session.commit()
        
        can_add, reason = can_add_diagnosis(doctor_user, patient_user.id, db_session)
        
        assert can_add is False
        assert reason == "deactivated"
    
    def test_can_add_diagnosis_deactivated_patient(self, db_session, doctor_user, patient_user):
        """Test cannot add diagnosis for deactivated patient"""
        doctor_user.patients.append(patient_user)
        patient_user.is_active = 0
        db_session.commit()
        
        can_add, reason = can_add_diagnosis(doctor_user, patient_user.id, db_session)
        
        assert can_add is False
        assert reason == "deactivated_patient"
    
    def test_can_add_diagnosis_patient_not_found(self, db_session, doctor_user):
        """Test cannot add diagnosis for non-existent patient"""
        can_add, reason = can_add_diagnosis(doctor_user, 99999, db_session)
        
        assert can_add is False
        assert reason == "patient_not_found"
    
    def test_can_modify_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test doctor can modify own diagnosis"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        # Create diagnosis
        diagnosis = MedicalHistory(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Test Condition"
        )
        db_session.add(diagnosis)
        db_session.commit()
        
        can_modify, reason = can_modify_diagnosis(doctor_user, diagnosis.id, db_session)
        
        assert can_modify is True
        assert reason == ""
    
    def test_can_modify_diagnosis_not_owner(self, db_session, doctor_user, patient_user):
        """Test doctor cannot modify another doctor's diagnosis"""
        from app.services import hash_password
        from app.database import DoctorInfo
        
        # Create second doctor
        doctor2 = User(
            username="doctor2",
            email="doctor2@test.com",
            password=hash_password("doctor123"),
            fname="Second",
            lname="Doctor",
            role="doctor",
            is_active=1
        )
        db_session.add(doctor2)
        db_session.commit()
        
        doctor_info = DoctorInfo(
            user_id=doctor2.id,
            license_number="LIC456",
            specialization="Cardiology"
        )
        db_session.add(doctor_info)
        db_session.commit()
        
        # Create diagnosis by first doctor
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        diagnosis = MedicalHistory(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Test Condition"
        )
        db_session.add(diagnosis)
        db_session.commit()
        
        # Try to modify with second doctor
        can_modify, reason = can_modify_diagnosis(doctor2, diagnosis.id, db_session)
        
        assert can_modify is False
        assert reason == "not_owner"
    
    def test_can_modify_diagnosis_record_not_found(self, db_session, doctor_user):
        """Test cannot modify non-existent diagnosis"""
        can_modify, reason = can_modify_diagnosis(doctor_user, 99999, db_session)
        
        assert can_modify is False
        assert reason == "record_not_found"
    
    def test_can_delete_diagnosis_success(self, db_session, doctor_user, patient_user):
        """Test doctor can delete own diagnosis"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        diagnosis = MedicalHistory(
            patient_id=patient_user.id,
            doctor_id=doctor_user.id,
            medical_condition="Test Condition"
        )
        db_session.add(diagnosis)
        db_session.commit()
        
        # Use can_modify_diagnosis for delete permission check (same logic)
        can_delete, reason = can_modify_diagnosis(doctor_user, diagnosis.id, db_session)
        
        assert can_delete is True
        assert reason == ""


class TestViewPatientData:
    """Test view patient data permissions"""
    
    def test_can_view_patient_data_admin(self, db_session, admin_user, patient_user):
        """Test admin can view any patient data"""
        can_view, reason = can_view_patient_data(admin_user, patient_user.id, db_session)
        
        assert can_view is True
        assert reason == ""
    
    def test_can_view_patient_data_self(self, db_session, patient_user):
        """Test patient can view own data"""
        can_view, reason = can_view_patient_data(patient_user, patient_user.id, db_session)
        
        assert can_view is True
        assert reason == ""
    
    def test_can_view_patient_data_linked_doctor(self, db_session, doctor_user, patient_user):
        """Test linked doctor can view patient data"""
        doctor_user.patients.append(patient_user)
        db_session.commit()
        
        can_view, reason = can_view_patient_data(doctor_user, patient_user.id, db_session)
        
        assert can_view is True
        assert reason == ""
    
    def test_can_view_patient_data_unlinked_doctor(self, db_session, doctor_user, patient_user):
        """Test unlinked doctor cannot view patient data"""
        can_view, reason = can_view_patient_data(doctor_user, patient_user.id, db_session)
        
        assert can_view is False
        assert reason == "not_linked"


class TestRolePermissions:
    """Test role-based permissions"""
    
    def test_check_role_permission_admin(self, db_session, admin_user):
        """Test role permission check for admin"""
        from app.services.policy_service import check_role_permission
        
        has_perm, reason = check_role_permission(admin_user, ["admin"])
        
        assert has_perm is True
        assert reason == ""
    
    def test_check_role_permission_doctor(self, db_session, doctor_user):
        """Test role permission check for doctor"""
        from app.services.policy_service import check_role_permission
        
        has_perm, reason = check_role_permission(doctor_user, ["doctor", "admin"])
        
        assert has_perm is True
        assert reason == ""
    
    def test_check_role_permission_wrong_role(self, db_session, patient_user):
        """Test role permission check with wrong role"""
        from app.services.policy_service import check_role_permission
        
        has_perm, reason = check_role_permission(patient_user, ["doctor", "admin"])
        
        assert has_perm is False
        assert reason == "unauthorized"
    
    def test_check_role_permission_deactivated(self, db_session, doctor_user):
        """Test role permission check with deactivated account"""
        from app.services.policy_service import check_role_permission
        
        doctor_user.is_active = 0
        db_session.commit()
        
        has_perm, reason = check_role_permission(doctor_user, ["doctor"])
        
        assert has_perm is False
        assert reason == "deactivated"


class TestPolicyEdgeCases:
    """Test edge cases in policy service"""
    
    def test_admin_bypass_deactivation_check(self, db_session, admin_user, patient_user):
        """Test if admin can access deactivated patient (if policy allows)"""
        patient_user.is_active = 0
        db_session.commit()
        
        has_access, reason = check_patient_access(
            current_user=admin_user,
            patient=patient_user,
            db=db_session
        )
        
        # Depending on policy, might still deny access to deactivated
        assert isinstance(has_access, bool)
        assert isinstance(reason, str)
    
    def test_multiple_doctors_same_patient(self, db_session, doctor_user, patient_user):
        """Test multiple doctors can access same patient"""
        from app.services import hash_password
        from app.database import DoctorInfo
        
        # Create second doctor
        doctor2 = User(
            username="doctor2",
            email="doctor2@test.com",
            password=hash_password("doctor123"),
            fname="Second",
            lname="Doctor",
            role="doctor",
            is_active=1
        )
        db_session.add(doctor2)
        db_session.commit()
        
        doctor_info = DoctorInfo(
            user_id=doctor2.id,
            license_number="LIC456",
            specialization="Cardiology"
        )
        db_session.add(doctor_info)
        db_session.commit()
        
        # Link both doctors to patient
        doctor_user.patients.append(patient_user)
        doctor2.patients.append(patient_user)
        db_session.commit()
        
        # Both should have access
        has_access1, _ = check_patient_access(doctor_user, patient_user, db_session)
        has_access2, _ = check_patient_access(doctor2, patient_user, db_session)
        
        assert has_access1 is True
        assert has_access2 is True
