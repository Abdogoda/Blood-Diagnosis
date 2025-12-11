# 🩸 Blood Diagnosis System

A comprehensive web-based medical platform for blood test analysis with AI-powered diagnostics. The system facilitates interaction between patients, doctors, and administrators while providing automated CBC (Complete Blood Count) analysis for anemia detection.

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [User Roles & Features](#-user-roles--features)
- [API Structure](#-api-structure)
- [AI/ML Module](#-aiml-module)
- [Directory Structure](#-directory-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

### Core Features

- 🔐 **Secure Authentication & Authorization** - Role-based access control (Admin, Doctor, Patient)
- 🤖 **AI-Powered CBC Analysis** - Automated anemia detection using TabNet neural network
- 📊 **Blood Test Management** - Upload, view, and analyze blood test results
- 👥 **Patient Management** - Comprehensive patient profiles and medical history
- 💬 **Messaging System** - Secure communication between doctors and patients
- 📱 **Responsive UI** - Mobile-friendly interface built with modern HTML/CSS/JavaScript
- 📈 **Dashboard Analytics** - Real-time statistics and insights
- 🖼️ **Image Processing** - Blood cell image analysis capabilities
- 📄 **Report Generation** - Automated medical reports with AI predictions
- 🔒 **Password Reset** - Secure password recovery system
- 📧 **Email Notifications** - Automated email alerts for test results

### AI Capabilities

- **Anemia Detection** - ML model trained on CBC parameters
- **Feature Normalization** - Automatic data preprocessing and scaling
- **Flexible Input** - Supports various CBC parameter naming conventions
- **Confidence Scoring** - Probability-based predictions with confidence levels

---

## 🛠 Technology Stack

### Backend

- **Framework**: FastAPI 0.124.0
- **Language**: Python 3.12
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + bcrypt password hashing
- **Template Engine**: Jinja2

### AI/ML

- **Deep Learning**: PyTorch 2.2.0
- **ML Framework**: PyTorch-TabNet 4.1.0
- **Data Processing**: pandas, numpy, scikit-learn
- **Image Processing**: OpenCV 4.8.1

### Frontend

- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Vanilla JS with async/await patterns
- **Bootstrap** - UI components (via templates)

### Development Tools

- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Linting**: Built-in Python standards
- **Version Control**: Git

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
│              (HTML/CSS/JavaScript)                       │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP/HTTPS
┌───────────────────▼─────────────────────────────────────┐
│                  FastAPI Application                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Routers   │  │  Services   │  │     AI      │    │
│  │             │  │             │  │   Models    │    │
│  │ • Auth      │  │ • Auth      │  │             │    │
│  │ • Admin     │  │ • Patient   │  │ • CBC       │    │
│  │ • Doctor    │  │ • Medical   │  │ • Predict   │    │
│  │ • Patient   │  │ • Message   │  │             │    │
│  │ • Public    │  │ • AI Svc    │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                           │                              │
│                  ┌────────▼────────┐                    │
│                  │   SQLAlchemy    │                    │
│                  │      ORM        │                    │
│                  └────────┬────────┘                    │
└───────────────────────────┼─────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   PostgreSQL    │
                   │    Database     │
                   └─────────────────┘
```

---

## 📦 Prerequisites

Before installation, ensure you have:

- **Python 3.12** or higher
- **PostgreSQL** database server (version 12+)
- **pip** package manager
- **Git** (optional, for cloning)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Operating System Support

- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+, Debian, CentOS)
- ✅ macOS 11+

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/blood-diagnosis.git
cd blood-diagnosis
```

### 2. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Application Settings
APP_NAME="Blood Diagnosis System"
APP_VERSION="1.0.0"
SECRET_KEY="your-super-secret-key-change-this-in-production"

# Database Configuration
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/blood_diagnosis_db"

# JWT Settings
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Settings
MAX_UPLOAD_SIZE_MB=10
UPLOAD_DIR="uploads"

# AI Model Settings
AI_MODEL_ENABLED=true
AI_MODEL_PATH="app/ai/cbc/tabnet_anemia_model.zip"

# Email Configuration (Optional)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
```

---

## ⚙ Configuration

### Database Configuration

Edit `app/database.py` to configure your database connection:

```python
DATABASE_URL = "postgresql://username:password@host:port/database_name"
```

### AI Model Configuration

The AI model files should be located in `app/ai/cbc/`:

- `tabnet_anemia_model.zip` - Trained TabNet model
- `scaler.pkl` - Feature scaler
- `used_features.json` - Feature configuration

---

## 🗄 Database Setup

### 1. Create PostgreSQL Database

```sql
CREATE DATABASE blood_diagnosis_db;
```

### 2. Initialize Database Schema

Run the database initialization script:

```bash
python init_db.py
```

This will:

- Create all required tables
- Set up relationships
- Seed initial data (admin user, AI models)

### 3. Create Admin User (Alternative Method)

If you need to create an admin user separately:

```bash
python create_admin.py
```

Follow the interactive prompts to set up your admin account.

### Database Schema

**Main Tables:**

- `users` - User accounts (patients, doctors, admins)
- `doctor_info` - Doctor-specific information
- `doctor_patients` - Many-to-many relationship table
- `blood_tests` - Blood test records
- `test_results` - Test result data
- `medical_history` - Patient medical history
- `messages` - Internal messaging system
- `models` - AI model metadata

---

## ▶ Running the Application

### Using the Build Script (Recommended)

The application includes an interactive build script:

```bash
# On Linux/Mac:
./build.sh

# On Windows (Git Bash or WSL):
bash build.sh
```

The script provides options for:

1. **Quick Start** - Install dependencies and run
2. **Full Setup** - Complete installation with database initialization
3. **Development Mode** - Run with auto-reload
4. **Production Mode** - Optimized production server
5. **Run Tests** - Execute test suite
6. **Database Reset** - Reinitialize database

### Manual Start

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the Application

Once running, access the application at:

- **Homepage**: http://localhost:8000
- **Login**: http://localhost:8000/auth/login
- **Admin Dashboard**: http://localhost:8000/admin/dashboard
- **Doctor Dashboard**: http://localhost:8000/doctors/dashboard
- **Patient Dashboard**: http://localhost:8000/patients/dashboard
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 👥 User Roles & Features

### 🔴 Admin Role

**Access:** `/admin/*`

**Capabilities:**

- 👤 **User Management**

  - View all users (doctors and patients)
  - Activate/deactivate accounts
  - View detailed user profiles
  - Monitor user activity

- 📊 **Dashboard Analytics**

  - Total users statistics
  - Active users count
  - Test submission metrics
  - System health monitoring

- 🔬 **AI Model Management**

  - View active AI models
  - Model performance metrics
  - Model version control

- 💬 **Message Management**

  - View all system messages
  - Monitor doctor-patient communications
  - Message filtering and search

- 📈 **Reports**
  - Generate system reports
  - View test statistics
  - Export data

### 🔵 Doctor Role

**Access:** `/doctors/*`

**Capabilities:**

- 👨‍⚕️ **Patient Management**

  - View assigned patients
  - Access patient profiles
  - Review medical history
  - Add medical notes

- 🩺 **Test Review**

  - View patient blood tests
  - Review AI predictions
  - Validate test results
  - Add professional interpretation

- 💬 **Communication**

  - Send messages to patients
  - Respond to patient queries
  - Receive test notifications

- 📊 **Dashboard**

  - Overview of assigned patients
  - Recent test submissions
  - Pending reviews
  - Performance statistics

- 👤 **Profile Management**
  - Update professional information
  - Set specialization
  - Manage contact details

### 🟢 Patient Role

**Access:** `/patients/*`

**Capabilities:**

- 🔬 **Test Management**

  - Upload CBC test results (CSV format)
  - Upload blood cell images
  - View test history
  - Track test status

- 🤖 **AI Analysis**

  - Receive automated anemia predictions
  - View confidence scores
  - Get health recommendations
  - Understand test interpretations

- 📋 **Medical History**

  - View complete medical records
  - Track health trends over time
  - Export medical history

- 💬 **Doctor Communication**

  - Send messages to assigned doctors
  - Receive medical advice
  - Ask questions about results

- 📊 **Dashboard**

  - Health status overview
  - Recent test results
  - AI predictions summary
  - Upcoming appointments

- 👤 **Profile Management**
  - Update personal information
  - Manage blood type information
  - Update contact details
  - Upload profile picture

---

## 🌐 API Structure

### Authentication Endpoints

```
POST   /auth/register          - Register new user
POST   /auth/login             - User login
GET    /auth/logout            - User logout
POST   /auth/reset-password    - Request password reset
POST   /auth/confirm-reset     - Confirm password reset
```

### Admin Endpoints

```
GET    /admin/dashboard        - Admin dashboard
GET    /admin/doctors          - List all doctors
GET    /admin/patients         - List all patients
GET    /admin/doctor/{id}      - Doctor details
GET    /admin/patient/{id}     - Patient details
POST   /admin/user/{id}/toggle - Activate/deactivate user
GET    /admin/messages         - View all messages
GET    /admin/models           - View AI models
```

### Doctor Endpoints

```
GET    /doctors/dashboard      - Doctor dashboard
GET    /doctors/patients       - List assigned patients
GET    /doctors/patient/{id}   - Patient profile
GET    /doctors/test/{id}      - View test details
POST   /doctors/message        - Send message to patient
GET    /doctors/account        - Doctor account settings
POST   /doctors/account/update - Update doctor profile
```

### Patient Endpoints

```
GET    /patients/dashboard          - Patient dashboard
GET    /patients/tests              - List all tests
GET    /patients/test/{id}          - Test details
POST   /patients/upload/cbc         - Upload CBC test
POST   /patients/upload/blood-cell  - Upload blood cell image
GET    /patients/medical-history    - Medical history
GET    /patients/reports            - View reports
POST   /patients/message            - Send message to doctor
GET    /patients/account            - Account settings
POST   /patients/account/update     - Update patient profile
```

### Public Endpoints

```
GET    /                       - Homepage
GET    /about                  - About page
GET    /contact                - Contact page
GET    /services               - Services page
GET    /docs                   - API documentation (Swagger)
GET    /redoc                  - API documentation (ReDoc)
```

---

## 🤖 AI/ML Module

### CBC Anemia Prediction

The system uses a **TabNet neural network** for anemia detection based on Complete Blood Count (CBC) parameters.

#### Model Architecture

- **Algorithm**: TabNet (Attentive Interpretable Tabular Learning)
- **Framework**: PyTorch + pytorch_tabnet
- **Input Features**: 10 CBC parameters
- **Output**: Binary classification (Anemia / No Anemia) with probability

#### Supported CBC Parameters

| Parameter   | Aliases                     | Description                               |
| ----------- | --------------------------- | ----------------------------------------- |
| **RBC**     | rbc, red blood cells        | Red Blood Cell count                      |
| **HGB**     | hgb, hb, hemoglobin         | Hemoglobin level                          |
| **HCT/PCV** | hct, pcv, hematocrit        | Hematocrit/Packed Cell Volume             |
| **MCV**     | mcv                         | Mean Corpuscular Volume                   |
| **MCH**     | mch                         | Mean Corpuscular Hemoglobin               |
| **MCHC**    | mchc                        | Mean Corpuscular Hemoglobin Concentration |
| **RDW**     | rdw, rdw-cv                 | Red Cell Distribution Width               |
| **TLC/WBC** | tlc, wbc, white blood cells | White Blood Cell count                    |
| **PLT**     | plt, platelets              | Platelet count                            |
| **Age**     | age, years                  | Patient age                               |

#### Usage Example

```python
from app.services.ai_service import cbc_prediction_service

# Predict from CSV file
result = await cbc_prediction_service.predict_from_csv(
    file_path="uploads/tests/cbc/test_123.csv"
)

# Result structure:
# {
#     "prediction": "Anemia" or "No Anemia",
#     "confidence": 0.95,  # 95% confidence
#     "probabilities": {
#         "Anemia": 0.95,
#         "No Anemia": 0.05
#     },
#     "features_used": [...],
#     "interpretation": "High confidence anemia detection..."
# }
```

#### Model Performance

- **Accuracy**: ~95% (on validation set)
- **Inference Time**: < 100ms per prediction
- **Memory Usage**: ~200MB (model loaded in RAM)

#### Supported Input Formats

**CSV Format:**

```csv
Parameter,Value
RBC,4.5
HGB,13.2
HCT,39.5
MCV,87.8
MCH,29.3
MCHC,33.4
RDW,13.1
WBC,7200
PLT,250000
Age,35
```

**Alternative CSV Format (with aliases):**

```csv
Red Blood Cells,Hemoglobin,Hematocrit,MCV,MCH,MCHC,RDW-CV,White Blood Cells,Platelets,Age
4.5,13.2,39.5,87.8,29.3,33.4,13.1,7200,250000,35
```

---

## 📁 Directory Structure

```
blood-diagnosis/
├── app/                          # Main application directory
│   ├── main.py                   # FastAPI application entry point
│   ├── database.py               # Database models and configuration
│   ├── __init__.py
│   │
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── admin.py              # Admin routes
│   │   ├── auth.py               # Authentication routes
│   │   ├── doctors.py            # Doctor routes
│   │   ├── patients.py           # Patient routes
│   │   └── public.py             # Public routes
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py         # AI/ML integration
│   │   ├── auth_service.py       # Authentication logic
│   │   ├── patient_service.py    # Patient management
│   │   ├── medical_history_service.py
│   │   ├── message_service.py    # Messaging system
│   │   ├── policy_service.py     # Authorization policies
│   │   ├── profile_service.py    # User profiles
│   │   └── ui_service.py         # UI utilities
│   │
│   ├── models/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py            # Data validation models
│   │
│   ├── ai/                       # AI/ML modules
│   │   └── cbc/                  # CBC analysis
│   │       ├── __init__.py
│   │       ├── predict.py        # Prediction logic
│   │       ├── used_features.json
│   │       ├── tabnet_anemia_model.zip
│   │       └── scaler.pkl
│   │
│   ├── static/                   # Static assets
│   │   ├── css/                  # Stylesheets
│   │   │   ├── base.css
│   │   │   ├── main.css
│   │   │   ├── error.css
│   │   │   └── print.css
│   │   ├── js/                   # JavaScript files
│   │   │   ├── admin_dashboard.js
│   │   │   ├── admin_doctors.js
│   │   │   ├── base.js
│   │   │   ├── cbc_results.js
│   │   │   ├── cbc_upload.js
│   │   │   ├── image_upload.js
│   │   │   ├── register.js
│   │   │   └── main.js
│   │   └── img/                  # Images
│   │
│   └── templates/                # Jinja2 templates
│       ├── base.html
│       ├── admin/                # Admin templates
│       ├── auth/                 # Authentication templates
│       ├── doctor/               # Doctor templates
│       ├── patient/              # Patient templates
│       ├── public/               # Public templates
│       ├── errors/               # Error pages
│       ├── layouts/              # Layout templates
│       └── shared/               # Shared components
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   ├── test_admin_routes.py
│   ├── test_ai_service.py
│   ├── test_auth_routes.py
│   ├── test_auth_service.py
│   ├── test_database_models.py
│   ├── test_doctor_routes.py
│   ├── test_medical_history_service.py
│   ├── test_message_service.py
│   ├── test_patient_routes.py
│   ├── test_patient_service.py
│   ├── test_policy_service.py
│   ├── test_profile_service.py
│   ├── test_public_routes.py
│   └── test_ui_service.py
│
├── uploads/                      # File uploads directory
│   ├── profiles/                 # Profile pictures
│   └── tests/                    # Test files
│       ├── cbc/                  # CBC test files
│       └── blood_cell/           # Blood cell images
│
├── build.sh                      # Interactive build script
├── init_db.py                    # Database initialization
├── create_admin.py               # Admin user creation
├── requirements.txt              # Python dependencies
├── pytest.ini                    # pytest configuration
├── .env                          # Environment variables (create this)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite covering all major components.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_admin"
```

### Test Coverage

The test suite covers:

- ✅ Authentication & Authorization
- ✅ User Management (Admin, Doctor, Patient)
- ✅ Blood Test Upload & Processing
- ✅ AI Prediction Service
- ✅ Medical History Management
- ✅ Messaging System
- ✅ Database Models & Relationships
- ✅ API Endpoints
- ✅ Service Layer Logic
- ✅ Policy Enforcement

### Test Configuration

Tests are configured in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
```

---

## 🚀 Deployment

### Production Deployment

#### 1. Environment Configuration

Ensure production environment variables are set:

```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
```

#### 2. Database Migration

```bash
# Backup existing database (if applicable)
pg_dump blood_diagnosis_db > backup.sql

# Run migrations
python init_db.py
```

#### 3. Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile access.log \
  --error-logfile error.log
```

#### 4. Using Docker

```dockerfile
# Dockerfile example
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t blood-diagnosis .
docker run -p 8000:8000 blood-diagnosis
```

#### 5. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/app/static;
    }

    location /uploads {
        alias /path/to/uploads;
    }
}
```

### Cloud Deployment Options

- **AWS**: EC2, RDS, S3
- **Heroku**: Web dyno + PostgreSQL addon
- **DigitalOcean**: Droplet + Managed PostgreSQL
- **Google Cloud**: Cloud Run + Cloud SQL
- **Azure**: App Service + Azure Database for PostgreSQL

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Run tests**
   ```bash
   pytest
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### Code Standards

- Follow PEP 8 style guide for Python code
- Write descriptive commit messages
- Add docstrings to functions and classes
- Include type hints where applicable
- Maintain test coverage above 80%

### Reporting Issues

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:

```bash
# Verify PostgreSQL is running
# Windows:
net start postgresql

# Linux:
sudo systemctl start postgresql

# Check connection settings in .env file
```

#### 2. AI Model Not Loading

**Problem**: `Warning: Could not load CBC model`

**Solution**:

```bash
# Ensure pytorch_tabnet is installed
pip install pytorch-tabnet

# Verify model files exist
ls app/ai/cbc/tabnet_anemia_model.zip
```

#### 3. Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:

```bash
# Run from project root directory
cd /path/to/blood-diagnosis

# Ensure PYTHONPATH includes current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 4. Port Already in Use

**Problem**: `[ERROR] [Errno 98] Address already in use`

**Solution**:

```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port:
uvicorn app.main:app --port 8001
```

#### 5. File Upload Issues

**Problem**: File uploads failing or not saving

**Solution**:

```bash
# Check uploads directory exists and has write permissions
mkdir -p uploads/tests/cbc uploads/tests/blood_cell uploads/profiles

# Set permissions (Linux/Mac):
chmod -R 755 uploads/
```

#### 6. JWT Token Errors

**Problem**: `JWTError: Signature verification failed`

**Solution**:

- Ensure `SECRET_KEY` in `.env` is consistent
- Check token expiration settings
- Clear browser cookies and login again

### Getting Help

If you encounter issues not listed here:

1. Check the [GitHub Issues](https://github.com/yourusername/blood-diagnosis/issues)
2. Review application logs in the terminal
3. Check `error.log` file (if using production mode)
4. Contact the development team

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

```
MIT License

Copyright (c) 2025 Blood Diagnosis System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📞 Contact & Support

- **Project Repository**: https://github.com/yourusername/blood-diagnosis
- **Issue Tracker**: https://github.com/yourusername/blood-diagnosis/issues
- **Documentation**: https://yourdomain.com/docs
- **Email**: support@yourdomain.com

---

## 🙏 Acknowledgments

- FastAPI framework and community
- PyTorch and pytorch_tabnet developers
- Open-source medical datasets used for AI training
- All contributors and testers

---

## 📚 Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyTorch TabNet](https://github.com/dreamquark-ai/tabnet)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tutorials

- Setting up FastAPI applications
- Building ML models with TabNet
- PostgreSQL database design
- JWT authentication implementation

### Related Projects

- Medical imaging analysis tools
- Healthcare management systems
- AI-powered diagnostic platforms

---

## 🔄 Version History

### Version 1.0.0 (Current)

- ✅ Initial release
- ✅ User authentication & authorization
- ✅ CBC anemia prediction
- ✅ Patient/Doctor/Admin dashboards
- ✅ Blood test upload & management
- ✅ Messaging system
- ✅ Medical history tracking
- ✅ Responsive web interface

### Planned Features (Future Versions)

- 🔜 Mobile application (iOS/Android)
- 🔜 Additional blood test analysis (lipid profile, liver function)
- 🔜 Appointment scheduling system
- 🔜 Video consultation integration
- 🔜 Advanced analytics & reports
- 🔜 Multi-language support
- 🔜 API rate limiting
- 🔜 Real-time notifications
- 🔜 Integration with lab equipment

---

<div align="center">

**Made with ❤️ for better healthcare**

⭐ Star this repository if you find it helpful!

</div>
