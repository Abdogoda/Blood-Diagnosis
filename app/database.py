# Database configuration and session management
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/blood_diagnosis_db"

engine = create_engine(
    DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for many-to-many relationship between doctors and patients
doctor_patients = Table(
    'doctor_patients',
    Base.metadata,
    Column('doctor_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('patient_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

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
    phone = Column(String(30))
    address = Column(Text)
    profile_image = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor_info = relationship("DoctorInfo", back_populates="user", uselist=False)
    
    # Many-to-many: doctors can have many patients
    patients = relationship(
        "User",
        secondary=doctor_patients,
        primaryjoin=id == doctor_patients.c.doctor_id,
        secondaryjoin=id == doctor_patients.c.patient_id,
        backref="doctors"
    )


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
    treatment = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_status = Column(String(20), default='pending', nullable=False)  # accepted, rejected, pending
    result = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    confidence = Column(Numeric(5,4), nullable=True)
    review_requested_from = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_requested_at = Column(DateTime, nullable=True)
    
    # Relationships
    test_files = relationship("TestFile", back_populates="test", cascade="all, delete-orphan")


class TestFile(Base):
    __tablename__ = "test_files"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    extension = Column(String(50), nullable=False)
    path = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # input, output
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    test = relationship("Test", back_populates="test_files")


class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    accuracy = Column(Numeric(5,2))
    tests_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0, nullable=False)  # 0=unread, 1=read
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


if __name__ == "__main__":
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
