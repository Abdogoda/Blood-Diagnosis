"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db, User, DoctorInfo

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    from app.services import hash_password
    user = User(
        username="admin",
        email="admin@test.com",
        password=hash_password("admin123"),
        fname="Admin",
        lname="User",
        role="admin",
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def doctor_user(db_session):
    """Create a doctor user for testing"""
    from app.services import hash_password
    user = User(
        username="doctor1",
        email="doctor@test.com",
        password=hash_password("doctor123"),
        fname="John",
        lname="Doe",
        role="doctor",
        phone="1234567890",
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    
    # Add doctor info
    doctor_info = DoctorInfo(
        user_id=user.id,
        license_number="LIC123",
        specialization="Hematology"
    )
    db_session.add(doctor_info)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def patient_user(db_session):
    """Create a patient user for testing"""
    from app.services import hash_password
    user = User(
        username="patient1",
        email="patient@test.com",
        password=hash_password("patient123"),
        fname="Jane",
        lname="Smith",
        role="patient",
        phone="0987654321",
        blood_type="A+",
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_admin(client, admin_user):
    """Get authentication headers for admin"""
    from app.services.auth_service import create_access_token
    
    token = create_access_token({"sub": admin_user.username, "role": admin_user.role})
    client.cookies.set("access_token", token)
    return {}  # Return empty dict since cookies are set on client


@pytest.fixture
def auth_headers_doctor(client, doctor_user):
    """Get authentication headers for doctor"""
    from app.services.auth_service import create_access_token
    
    token = create_access_token({"sub": doctor_user.username, "role": doctor_user.role})
    client.cookies.set("access_token", token)
    return {}  # Return empty dict since cookies are set on client


@pytest.fixture
def auth_headers_patient(client, patient_user):
    """Get authentication headers for patient"""
    from app.services.auth_service import create_access_token
    
    token = create_access_token({"sub": patient_user.username, "role": patient_user.role})
    client.cookies.set("access_token", token)
    return {}  # Return empty dict since cookies are set on client
