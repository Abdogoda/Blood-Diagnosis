# Authentication router
from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db, User, DoctorInfo
from app.models.schemas import UserCreate, UserResponse, Token, DoctorInfoCreate
from app.services import (
    verify_password, 
    hash_password,
    create_access_token,
    get_current_user,
    get_current_user_from_cookie,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Display login page."""
    if current_user:
        # Already logged in, redirect to dashboard
        if current_user.role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        elif current_user.role == "doctor":
            return RedirectResponse(url="/doctor/dashboard", status_code=303)
        else:
            return RedirectResponse(url="/patient/dashboard", status_code=303)
    
    # Check for success message from registration or password reset
    registered = request.query_params.get("registered")
    reset = request.query_params.get("reset")
    
    success = None
    if registered:
        success = "Registration successful! Please login with your credentials."
    elif reset == "success":
        success = "Password reset successful! Please login with your new password."
    
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "success": success
    })


@router.get("/register")
async def register_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Display registration page."""
    if current_user:
        # Already logged in, redirect to dashboard
        if current_user.role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        elif current_user.role == "doctor":
            return RedirectResponse(url="/doctor/dashboard", status_code=303)
        else:
            return RedirectResponse(url="/patient/dashboard", status_code=303)
    
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and redirect to appropriate dashboard.
    
    Args:
        request: HTTP request object
        email: Email from form
        password: Password from form
        db: Database session
        
    Returns:
        RedirectResponse: Redirect to dashboard based on role
    """
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == email) | (User.username == email)
    ).first()
    
    if not user or not verify_password(password, user.password):
        # Return to login page with error message
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Incorrect email or password"
            },
            status_code=400
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Determine redirect URL based on role
    if user.role == "admin":
        redirect_url = "/admin/dashboard"
    elif user.role == "doctor":
        redirect_url = "/doctor/dashboard"
    else:
        redirect_url = "/patient/dashboard"
    
    # Create response with redirect
    response = RedirectResponse(url=redirect_url, status_code=303)
    
    # Set cookie for browser-based auth
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response


@router.post("/api/login", response_model=Token)
async def api_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    API endpoint for authentication (returns JSON token).
    
    Args:
        form_data: OAuth2 form with username and password
        db: Database session
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Set cookie for browser-based auth
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(..., alias="confirm-password"),
    role: str = Form(...),
    gender: str = Form(...),
    blood_type: str = Form(...),
    phone: str = Form(None),
    address: str = Form(...),
    license_number: str = Form(None),
    specialization: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Register a new user via web form and redirect to login.
    
    Args:
        request: HTTP request object
        Form fields for user registration
        db: Database session
        
    Returns:
        RedirectResponse or template with error
    """
    # Use email username part as username if not provided
    username = email.split('@')[0]
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Passwords do not match"
            },
            status_code=400
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Username already registered"
            },
            status_code=400
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Email already registered"
            },
            status_code=400
        )
    
    # Validate role-specific requirements
    if role == "doctor" and (not license_number or not specialization):
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "License number and specialization are required for doctors"
            },
            status_code=400
        )
    
    # Create new user
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        password=hashed_password,
        fname=fname,
        lname=lname,
        gender=gender,
        role=role,
        blood_type=blood_type,
        phone=phone,
        address=address
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create doctor info if role is doctor
    if role == "doctor" and license_number and specialization:
        db_doctor_info = DoctorInfo(
            user_id=db_user.id,
            license_number=license_number,
            specialization=specialization
        )
        db.add(db_doctor_info)
        db.commit()
    
    # Redirect to login page with success message
    return RedirectResponse(url="/auth/login?registered=true", status_code=303)


@router.post("/api/register", response_model=UserResponse)
async def api_register(
    user_data: UserCreate,
    doctor_info: DoctorInfoCreate = None,
    db: Session = Depends(get_db)
):
    """
    API endpoint for user registration (returns JSON).
    
    Args:
        user_data: User registration data
        doctor_info: Optional doctor information (required if role is doctor)
        db: Database session
        
    Returns:
        UserResponse: The created user object
        
    Raises:
        HTTPException: If username/email exists or passwords don't match
    """
    # Validate passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role-specific requirements
    if user_data.role == "doctor" and not doctor_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor information is required for doctor registration"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        fname=user_data.fname,
        lname=user_data.lname,
        gender=user_data.gender,
        role=user_data.role,
        blood_type=user_data.blood_type
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create doctor info if role is doctor
    if user_data.role == "doctor" and doctor_info:
        db_doctor_info = DoctorInfo(
            user_id=db_user.id,
            license_number=doctor_info.license_number,
            specialization=doctor_info.specialization
        )
        db.add(db_doctor_info)
        db.commit()
    
    return db_user


@router.post("/logout")
async def logout():
    """
    Logout user by clearing the access token cookie and redirect to home.
    
    Returns:
        RedirectResponse: Redirect to home page
    """
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@router.get("/logout")
async def logout_get():
    """
    Logout user via GET request (for convenience).
    
    Returns:
        RedirectResponse: Redirect to home page
    """
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return current_user


@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        current_password: User's current password
        new_password: New password
        confirm_password: Confirmation of new password
        current_user: The authenticated user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If validation fails
    """
    # Verify current password
    if not verify_password(current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new passwords match
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Check password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password
    current_user.password = hash_password(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/reset-password")
async def reset_password_page(request: Request):
    """Display password reset request page."""
    return templates.TemplateResponse("auth/reset_password.html", {"request": request})


@router.post("/reset-password-request")
async def reset_password_request(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle password reset request.
    For simplicity, we'll generate a token and store it in the database.
    In production, you would send an email with the reset link.
    """
    import secrets
    from datetime import datetime, timedelta
    from app.database import PasswordResetToken
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return templates.TemplateResponse("auth/reset_password.html", {
            "request": request,
            "success": "If that email exists, a password reset link has been sent."
        })
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Delete any existing unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == 0
    ).delete()
    
    # Create new reset token (expires in 1 hour)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=0
    )
    db.add(reset_token)
    db.commit()
    
    # In production, send email with reset link: /auth/reset-password-confirm?token={token}
    # For now, we'll show a success message
    
    return templates.TemplateResponse("auth/reset_password.html", {
        "request": request,
        "success": f"Password reset link: /auth/reset-password-confirm?token={token} (Copy this link)"
    })


@router.get("/reset-password-confirm")
async def reset_password_confirm_page(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """Display password reset confirmation page with token."""
    from app.database import PasswordResetToken
    from datetime import datetime
    
    # Verify token exists and is valid
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == 0,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return templates.TemplateResponse("auth/reset_password_confirm.html", {
            "request": request,
            "error": "Invalid or expired reset token",
            "token": ""
        })
    
    return templates.TemplateResponse("auth/reset_password_confirm.html", {
        "request": request,
        "token": token
    })


@router.post("/reset-password-confirm")
async def reset_password_confirm(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Confirm password reset and update user password.
    """
    from app.database import PasswordResetToken
    from datetime import datetime
    
    # Verify passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse("auth/reset_password_confirm.html", {
            "request": request,
            "error": "Passwords do not match",
            "token": token
        }, status_code=400)
    
    # Check password length
    if len(new_password) < 8:
        return templates.TemplateResponse("auth/reset_password_confirm.html", {
            "request": request,
            "error": "Password must be at least 8 characters long",
            "token": token
        }, status_code=400)
    
    # Verify token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == 0,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return templates.TemplateResponse("auth/reset_password_confirm.html", {
            "request": request,
            "error": "Invalid or expired reset token",
            "token": ""
        }, status_code=400)
    
    # Get user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        return templates.TemplateResponse("auth/reset_password_confirm.html", {
            "request": request,
            "error": "User not found",
            "token": ""
        }, status_code=404)
    
    # Update password
    user.password = hash_password(new_password)
    
    # Mark token as used
    reset_token.used = 1
    
    db.commit()
    
    # Redirect to login with success message
    return RedirectResponse(url="/auth/login?reset=success", status_code=303)
