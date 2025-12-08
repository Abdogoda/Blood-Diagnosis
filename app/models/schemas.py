from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    fname: str = Field(..., min_length=1, max_length=100)
    lname: str = Field(..., min_length=1, max_length=100)
    gender: Optional[str] = Field(None, max_length=10)
    role: str = Field(..., pattern="^(admin|doctor|patient)$")
    blood_type: Optional[str] = Field(None, max_length=3)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# Doctor Schemas
class DoctorInfoCreate(BaseModel):
    license_number: str = Field(..., min_length=1, max_length=100)
    specialization: str = Field(..., min_length=1, max_length=150)


class DoctorInfoResponse(BaseModel):
    user_id: int
    license_number: str
    specialization: str

    class Config:
        from_attributes = True


# AI Prediction Schemas
class CBCInput(BaseModel):
    id: Optional[str] = None
    RBC: float
    HGB: float
    PCV: float
    MCV: float
    MCH: float
    MCHC: float
    TLC: float
    PLT: float
    RDW: Optional[float] = None