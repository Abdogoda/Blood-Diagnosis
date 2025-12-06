from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db, User
from app.services.jwt_utils import verify_token
from app.models.schemas import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the JWT token (for API routes).
    
    Args:
        token: The JWT token from the request
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from cookie (for template routes).
    
    Args:
        request: The HTTP request object
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    token_data = verify_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user_from_cookie)) -> User:
    """
    Ensure the current user is active (additional check for future use).
    
    Args:
        current_user: The current user from get_current_user
        
    Returns:
        User: The active user object
    """
    # Add any additional checks here (e.g., is_active field)
    return current_user


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to check if user has required role.
    
    Args:
        allowed_roles: List of allowed roles (e.g., ["admin", "doctor"])
        
    Returns:
        Function: A dependency function that validates user role
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for specific roles
def require_admin(current_user: User = Depends(require_role(["admin"]))) -> User:
    """Require admin role."""
    return current_user


def require_doctor(current_user: User = Depends(require_role(["admin", "doctor"]))) -> User:
    """Require doctor or admin role."""
    return current_user


def require_patient(current_user: User = Depends(require_role(["admin", "patient"]))) -> User:
    """Require patient or admin role."""
    return current_user


# Optional authentication for templates
async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get current user from session/cookie if available (for template rendering).
    Returns None if not authenticated.
    
    Args:
        request: The HTTP request object
        db: Database session
        
    Returns:
        Optional[User]: The user object if authenticated, None otherwise
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    token_data = verify_token(token)
    if token_data is None or token_data.username is None:
        return None
    
    user = db.query(User).filter(User.username == token_data.username).first()
    return user
