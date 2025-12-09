"""Profile management service for handling common user profile operations"""
from fastapi import Form, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import User
from app.services.auth_service import verify_password, hash_password
from app.services.ui_service import set_flash_message
from pathlib import Path
import uuid
import os


async def update_user_profile(
    current_user: User,
    db: Session,
    fname: str,
    lname: str,
    email: str,
    phone: str = None,
    address: str = None,
    redirect_url: str = "/account"
) -> tuple[bool, str]:
    """
    Update user profile information
    
    Args:
        current_user: The current logged-in user
        db: Database session
        fname: First name
        lname: Last name
        email: Email address
        phone: Phone number (optional)
        address: Address (optional)
        redirect_url: URL to redirect after operation
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Check if email already exists for another user
    existing_user = db.query(User).filter(
        User.email == email, 
        User.id != current_user.id
    ).first()
    
    if existing_user:
        return False, "Email already exists for another user"
    
    # Update user information
    current_user.fname = fname
    current_user.lname = lname
    current_user.email = email
    current_user.phone = phone
    current_user.address = address
    
    db.commit()
    db.refresh(current_user)
    
    return True, "Profile updated successfully!"


async def update_doctor_profile(
    current_user: User,
    db: Session,
    fname: str,
    lname: str,
    email: str,
    phone: str = None,
    address: str = None,
    specialization: str = None,
    redirect_url: str = "/doctor/account"
) -> tuple[bool, str]:
    """
    Update doctor profile information (includes specialization)
    
    Args:
        current_user: The current logged-in user (doctor)
        db: Database session
        fname: First name
        lname: Last name
        email: Email address
        phone: Phone number (optional)
        address: Address (optional)
        specialization: Doctor's specialization (optional)
        redirect_url: URL to redirect after operation
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Check if email already exists for another user
    existing_user = db.query(User).filter(
        User.email == email, 
        User.id != current_user.id
    ).first()
    
    if existing_user:
        return False, "Email already exists for another user"
    
    # Update user information
    current_user.fname = fname
    current_user.lname = lname
    current_user.email = email
    current_user.phone = phone
    current_user.address = address
    
    # Update doctor info
    if specialization:
        doctor_info = current_user.doctor_info
        if doctor_info:
            doctor_info.specialization = specialization
        else:
            from app.database import DoctorInfo
            new_doctor_info = DoctorInfo(
                user_id=current_user.id,
                license_number="TEMP-" + str(current_user.id),
                specialization=specialization
            )
            db.add(new_doctor_info)
    
    db.commit()
    db.refresh(current_user)
    
    return True, "Profile updated successfully!"


async def change_user_password(
    current_user: User,
    db: Session,
    current_password: str,
    new_password: str,
    confirm_password: str
) -> tuple[bool, str]:
    """
    Change user password with validation
    
    Args:
        current_user: The current logged-in user
        db: Database session
        current_password: Current password for verification
        new_password: New password
        confirm_password: Confirmation of new password
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Verify current password
    if not verify_password(current_password, current_user.password):
        return False, "Current password is incorrect"
    
    # Check if new passwords match
    if new_password != confirm_password:
        return False, "New passwords do not match"
    
    # Check password length
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Update password
    current_user.password = hash_password(new_password)
    db.commit()
    
    return True, "Password changed successfully!"


async def upload_user_profile_image(
    current_user: User,
    db: Session,
    profile_image: UploadFile
) -> tuple[bool, str]:
    """
    Upload and update user profile image
    
    Args:
        current_user: The current logged-in user
        db: Database session
        profile_image: Uploaded image file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_ext = os.path.splitext(profile_image.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return False, "Invalid file type. Only JPG, PNG, and GIF are allowed"
    
    # Create uploads/profiles directory if it doesn't exist
    upload_dir = Path("uploads/profiles")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Delete old profile image if exists
    if current_user.profile_image:
        old_file = Path(current_user.profile_image)
        if old_file.exists():
            old_file.unlink()
    
    # Save new file
    with open(file_path, "wb") as buffer:
        content = await profile_image.read()
        buffer.write(content)
    
    # Update user profile_image path
    current_user.profile_image = str(file_path)
    db.commit()
    
    return True, "Profile image updated successfully!"
