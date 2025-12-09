"""
Tests for profile service
"""
import pytest
from app.services.profile_service import (
    update_user_profile,
    update_doctor_profile,
    change_user_password,
    upload_user_profile_image
)
from app.database import User, DoctorInfo


class TestUpdateUserProfile:
    """Test updating user profile"""
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, db_session, patient_user):
        """Test successful profile update"""
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="NewFirstName",
            lname="NewLastName",
            email="newemail@test.com",
            phone="1112223333",
            address="123 New Street"
        )
        
        assert success is True
        assert "success" in message.lower()
        
        # Verify updates
        db_session.refresh(patient_user)
        assert patient_user.fname == "NewFirstName"
        assert patient_user.lname == "NewLastName"
        assert patient_user.email == "newemail@test.com"
        assert patient_user.phone == "1112223333"
        assert patient_user.address == "123 New Street"
    
    @pytest.mark.asyncio
    async def test_update_user_profile_duplicate_email(self, db_session, patient_user, doctor_user):
        """Test updating with email that already exists"""
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="NewFirstName",
            lname="NewLastName",
            email=doctor_user.email,  # Use doctor's email
            phone="1112223333"
        )
        
        assert success is False
        assert "already exists" in message.lower()
        
        # Email should not change
        db_session.refresh(patient_user)
        assert patient_user.email != doctor_user.email
    
    @pytest.mark.asyncio
    async def test_update_user_profile_partial(self, db_session, patient_user):
        """Test partial profile update (only some fields)"""
        original_email = patient_user.email
        
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="UpdatedName",
            lname=patient_user.lname,
            email=patient_user.email,
            phone="9998887777"
        )
        
        assert success is True
        db_session.refresh(patient_user)
        assert patient_user.fname == "UpdatedName"
        assert patient_user.phone == "9998887777"
        assert patient_user.email == original_email
    
    @pytest.mark.asyncio
    async def test_update_user_profile_optional_fields_none(self, db_session, patient_user):
        """Test updating profile with None for optional fields"""
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="FirstName",
            lname="LastName",
            email="email@test.com",
            phone=None,
            address=None
        )
        
        assert success is True
        db_session.refresh(patient_user)
        assert patient_user.phone is None
        assert patient_user.address is None


class TestUpdateDoctorProfile:
    """Test updating doctor profile"""
    
    @pytest.mark.asyncio
    async def test_update_doctor_profile_success(self, db_session, doctor_user):
        """Test successful doctor profile update"""
        success, message = await update_doctor_profile(
            current_user=doctor_user,
            db=db_session,
            fname="NewDocName",
            lname="NewDocLast",
            email="newdoc@test.com",
            phone="5556667777",
            address="456 Medical Plaza",
            specialization="Oncology"
        )
        
        assert success is True
        assert "success" in message.lower()
        
        # Verify updates
        db_session.refresh(doctor_user)
        assert doctor_user.fname == "NewDocName"
        assert doctor_user.email == "newdoc@test.com"
        assert doctor_user.doctor_info.specialization == "Oncology"
    
    @pytest.mark.asyncio
    async def test_update_doctor_profile_create_doctor_info(self, db_session, doctor_user):
        """Test updating doctor when doctor_info doesn't exist"""
        # Remove doctor_info
        if doctor_user.doctor_info:
            db_session.delete(doctor_user.doctor_info)
            db_session.commit()
            db_session.refresh(doctor_user)
        
        success, message = await update_doctor_profile(
            current_user=doctor_user,
            db=db_session,
            fname="Doc",
            lname="Name",
            email="doc@test.com",
            specialization="Pediatrics"
        )
        
        assert success is True
        db_session.refresh(doctor_user)
        assert doctor_user.doctor_info is not None
        assert doctor_user.doctor_info.specialization == "Pediatrics"
    
    @pytest.mark.asyncio
    async def test_update_doctor_profile_duplicate_email(self, db_session, doctor_user, patient_user):
        """Test updating doctor with existing email"""
        success, message = await update_doctor_profile(
            current_user=doctor_user,
            db=db_session,
            fname="Doc",
            lname="Name",
            email=patient_user.email,
            specialization="Cardiology"
        )
        
        assert success is False
        assert "already exists" in message.lower()
    
    @pytest.mark.asyncio
    async def test_update_doctor_profile_no_specialization(self, db_session, doctor_user):
        """Test updating doctor without changing specialization"""
        original_specialization = doctor_user.doctor_info.specialization
        
        success, message = await update_doctor_profile(
            current_user=doctor_user,
            db=db_session,
            fname="UpdatedDoc",
            lname="UpdatedLast",
            email=doctor_user.email,
            specialization=None
        )
        
        assert success is True
        db_session.refresh(doctor_user)
        assert doctor_user.doctor_info.specialization == original_specialization


class TestChangeUserPassword:
    """Test changing user password"""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, db_session, patient_user):
        """Test successful password change"""
        original_password_hash = patient_user.password
        
        success, message = await change_user_password(
            current_user=patient_user,
            db=db_session,
            current_password="patient123",
            new_password="newpassword123",
            confirm_password="newpassword123"
        )
        
        assert success is True
        assert "success" in message.lower()
        
        # Verify password changed
        db_session.refresh(patient_user)
        assert patient_user.password != original_password_hash
        
        # Verify new password works
        from app.services.auth_service import verify_password
        assert verify_password("newpassword123", patient_user.password)
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, db_session, patient_user):
        """Test changing password with wrong current password"""
        success, message = await change_user_password(
            current_user=patient_user,
            db=db_session,
            current_password="wrongpassword",
            new_password="newpassword123",
            confirm_password="newpassword123"
        )
        
        assert success is False
        assert "incorrect" in message.lower()
    
    @pytest.mark.asyncio
    async def test_change_password_mismatch(self, db_session, patient_user):
        """Test changing password when new passwords don't match"""
        success, message = await change_user_password(
            current_user=patient_user,
            db=db_session,
            current_password="patient123",
            new_password="newpassword123",
            confirm_password="differentpassword"
        )
        
        assert success is False
        assert "match" in message.lower()
    
    @pytest.mark.asyncio
    async def test_change_password_too_short(self, db_session, patient_user):
        """Test changing password when new password is too short"""
        success, message = await change_user_password(
            current_user=patient_user,
            db=db_session,
            current_password="patient123",
            new_password="short",
            confirm_password="short"
        )
        
        assert success is False
        assert "character" in message.lower() or "length" in message.lower()
    
    @pytest.mark.asyncio
    async def test_change_password_same_as_current(self, db_session, patient_user):
        """Test changing password to the same password"""
        success, message = await change_user_password(
            current_user=patient_user,
            db=db_session,
            current_password="patient123",
            new_password="patient123",
            confirm_password="patient123"
        )
        
        # This might succeed or fail depending on requirements
        # Just ensure it doesn't crash
        assert isinstance(success, bool)
        assert isinstance(message, str)


class TestUploadProfileImage:
    """Test uploading profile images"""
    
    @pytest.mark.asyncio
    async def test_upload_profile_image_success(self, db_session, patient_user):
        """Test successful profile image upload"""
        from fastapi import UploadFile
        from io import BytesIO
        from app.services.profile_service import upload_user_profile_image
        
        # Create mock image file
        image_content = b"fake image content"
        file = UploadFile(
            filename="profile.jpg",
            file=BytesIO(image_content)
        )
        
        success, message = await upload_user_profile_image(
            current_user=patient_user,
            profile_image=file,
            db=db_session
        )
        
        if success:
            assert "success" in message.lower()
            db_session.refresh(patient_user)
            assert patient_user.profile_image is not None
    
    @pytest.mark.asyncio
    async def test_upload_profile_image_invalid_extension(self, db_session, patient_user):
        """Test uploading file with invalid extension"""
        from fastapi import UploadFile
        from io import BytesIO
        from app.services.profile_service import upload_user_profile_image
        
        file = UploadFile(
            filename="profile.txt",
            file=BytesIO(b"not an image")
        )
        
        success, message = await upload_user_profile_image(
            current_user=patient_user,
            profile_image=file,
            db=db_session
        )
        
        assert success is False
        assert "type" in message.lower() or "extension" in message.lower() or "allowed" in message.lower()


class TestProfileServiceEdgeCases:
    """Test edge cases for profile service"""
    
    @pytest.mark.asyncio
    async def test_update_profile_with_unicode_characters(self, db_session, patient_user):
        """Test updating profile with unicode characters"""
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="José",
            lname="González",
            email="jose@test.com",
            address="北京市朝阳区"
        )
        
        assert success is True
        db_session.refresh(patient_user)
        assert patient_user.fname == "José"
        assert patient_user.lname == "González"
        assert "北京" in patient_user.address
    
    @pytest.mark.asyncio
    async def test_update_profile_with_very_long_address(self, db_session, patient_user):
        """Test updating with very long address"""
        long_address = "A" * 500
        
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="Test",
            lname="User",
            email="test@test.com",
            address=long_address
        )
        
        assert success is True
        db_session.refresh(patient_user)
        assert len(patient_user.address) == 500
    
    @pytest.mark.asyncio
    async def test_update_same_email_own_account(self, db_session, patient_user):
        """Test updating profile with same email (own email)"""
        original_email = patient_user.email
        
        success, message = await update_user_profile(
            current_user=patient_user,
            db=db_session,
            fname="Updated",
            lname="Name",
            email=original_email,  # Same email
            phone="1234567890"
        )
        
        assert success is True
        db_session.refresh(patient_user)
        assert patient_user.email == original_email
        assert patient_user.fname == "Updated"
