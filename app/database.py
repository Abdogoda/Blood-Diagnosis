# Database configuration and session management
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/blood_diagnosis_db"

engine = create_engine(
    DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    fname = Column(String(100), nullable=False)
    lname = Column(String(100), nullable=False)
    gender = Column(String(10))
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(10))
    blood_type = Column(String(3))
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    phones = relationship("UserPhone", back_populates="user")
    addresses = relationship("UserAddress", back_populates="user")
    doctor_info = relationship("DoctorInfo", back_populates="user", uselist=False)


class UserPhone(Base):
    __tablename__ = "user_phones"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    phone = Column(String(30), nullable=False)
    user = relationship("User", back_populates="phones")


class UserAddress(Base):
    __tablename__ = "user_addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    address = Column(Text, nullable=False)
    user = relationship("User", back_populates="addresses")


class DoctorInfo(Base):
    __tablename__ = "doctors_info"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    license_number = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(150), nullable=False)
    user = relationship("User", back_populates="doctor_info")


class MedicalHistory(Base):
    __tablename__ = "medical_history"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    medical_condition = Column(Text, nullable=False)
    diagnosis_date = Column(Date, nullable=False)
    treatment = Column(Text)
    notes = Column(Text)


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(150), nullable=False)
    description = Column(Text)
    test_time = Column(DateTime, nullable=False)


class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    result_time = Column(DateTime, nullable=False)
    result_value = Column(String(255), nullable=False)
    comment = Column(Text)


class TestFile(Base):
    __tablename__ = "test_files"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    file_name = Column(String(255))
    file_type = Column(String(50))
    file_path = Column(Text, nullable=False)
    uploaded_time = Column(DateTime, nullable=False)


class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    accuracy = Column(Numeric(5,2))


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"))
    result_id = Column(Integer, ForeignKey("test_results.id", ondelete="CASCADE"))
    confidence_score = Column(Numeric(5,4))
    comment = Column(Text)
    prediction_time = Column(DateTime, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

if __name__ == "__main__":
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
