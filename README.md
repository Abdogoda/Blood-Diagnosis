# 🩸 Blood Diagnosis System

A comprehensive web-based medical platform for blood test analysis with AI-powered diagnostics. The system facilitates interaction between patients, doctors, and administrators while providing automated CBC (Complete Blood Count) analysis for anemia detection.

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📋 Table of Contents

- [Build Script Guide](#-build-script-guide)
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

## 🛠 Build Script Guide

### Overview

The **Blood Diagnosis System** uses a powerful interactive build script (`build.sh`) that eliminates the need for manual command-line operations. Everything you need to install, configure, run, test, and deploy the application is accessible through an intuitive menu system.

### Why Use the Build Script?

✨ **No Commands to Remember** - All operations through a simple menu  
🔒 **Error Prevention** - Automatic validation and safety checks  
📊 **Visual Feedback** - Colored output showing success, warnings, and errors  
🔄 **Automated Workflows** - Complex operations done with one selection  
💾 **Safe Operations** - Automatic backups before destructive actions  
🌐 **ngrok Integration** - One-click public URL setup  

### Build Script Menu Structure

When you run `./build.sh`, you'll see three categories of options:

#### 🚀 QUICK START (Options 1-3)

Perfect for getting started quickly:

| Option | Name | Description | When to Use |
|--------|------|-------------|-------------|
| **1** | **Full Setup** | Complete first-time installation | First time setting up the project |
| **2** | **Run Application (Local)** | Start on local network with auto-reload | Development and local testing |
| **3** | **Run Application (ngrok)** | Start with public HTTPS URL | Sharing with remote users, demos |

#### ⚙️ SETUP & CONFIGURATION (Options 4-9)

Individual setup tasks:

| Option | Name | Description | When to Use |
|--------|------|-------------|-------------|
| **4** | **Install Dependencies** | Install Python packages from requirements.txt | After updating requirements, fixing package issues |
| **5** | **Setup Environment** | Create/update .env configuration file | Changing database settings, updating secrets |
| **6** | **Create Directories** | Create upload folders structure | After cleanup, fixing file upload issues |
| **7** | **Initialize Database** | Drop and recreate database tables | Fresh database, schema changes, fixing corruption |
| **8** | **Create Admin User** | Add new admin account | Creating first admin, adding more admins |
| **9** | **Setup ngrok** | Configure public URL tunneling | Before using Option 3, changing ngrok account |

#### 🔧 MAINTENANCE & TESTING (Options 10-12)

System maintenance and verification:

| Option | Name | Description | When to Use |
|--------|------|-------------|-------------|
| **10** | **Health Check** | Diagnose system status | Troubleshooting, verifying installation |
| **11** | **Run Tests** | Execute test suite with multiple options | Before deployment, after changes, CI/CD |
| **12** | **Clean/Reset** | Remove config and cache files | Fresh start, cleaning up after errors |

### Common Workflows

#### First Time Setup
```
1. Run ./build.sh
2. Select Option 1: Full Setup
3. Wait for installation to complete
4. Create admin account when prompted
5. Select Option 2: Run Application
6. Access http://localhost:8000
```

#### Daily Development
```
1. Run ./build.sh
2. Select Option 2: Run Application (Local)
3. Code and test (auto-reload active)
4. Press Ctrl+C to stop
```

#### Sharing Your Work
```
1. Run ./build.sh
2. Select Option 3: Run Application (ngrok)
3. Share the https://xxx.ngrok.io URL
4. Others can access your local app
```

#### Troubleshooting Issues
```
1. Run ./build.sh
2. Select Option 10: Health Check
3. Review what's wrong
4. Use suggested options to fix
```

#### Running Tests
```
1. Run ./build.sh
2. Select Option 11: Run Tests
3. Choose from 7 test options
4. View results and coverage
```

#### Complete Reset
```
1. Run ./build.sh
2. Select Option 12: Clean/Reset
3. Select Option 1: Full Setup
4. Fresh installation complete
```

### Build Script Features

#### 🎨 Colored Output
- 🟢 **Green** = Success messages
- 🔵 **Blue** = Informational messages
- 🟡 **Yellow** = Warnings
- 🔴 **Red** = Errors
- 🔵 **Cyan** = Headers and sections

#### 🛡️ Safety Features
- **Backup prompts** before database operations
- **Confirmation dialogs** for destructive actions
- **Port conflict detection** before starting server
- **Dependency verification** before running
- **PostgreSQL connection testing** before database ops

#### 📝 Detailed Logging
- Shows Python version in use
- Displays package installation progress
- Reports database operation status
- Indicates ngrok tunnel status
- Provides public URLs when available

### How to Run the Build Script

**On Linux/Mac:**
```bash
cd /path/to/blood-diagnosis
./build.sh
```

**On Windows (Git Bash):**
```bash
cd /path/to/blood-diagnosis
bash build.sh
```

**On Windows (WSL):**
```bash
cd /mnt/f/blood-diagnosis  # or your path
./build.sh
```

### Understanding Output Messages

**✓ Success Messages**
```
✓ Python: 3.12.0
✓ Dependencies installed successfully
✓ Database initialized successfully
```
Everything is working correctly.

**→ Info Messages**
```
→ Starting application on port 8000...
→ Creating backup: backup_20250608_143022.sql
```
Normal operations in progress.

**⚠ Warning Messages**
```
⚠ Port 8000 appears to be in use
⚠ .env file already exists
⚠ AI prediction features disabled
```
Non-critical issues that may need attention.

**✗ Error Messages**
```
✗ Failed to install dependencies
✗ Cannot connect to PostgreSQL
✗ Python not found
```
Critical issues that prevent operation.

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

### Quick Start with Build Script

The application includes an **interactive build script** (`build.sh`) that handles all installation, configuration, and deployment tasks. You don't need to run individual commands – the build script does everything for you!

### 1. Clone the Repository

Download the project to your local machine (or skip if you already have it).

### 2. Run the Build Script

**On Linux/Mac:**
```bash
./build.sh
```

**On Windows (using Git Bash, WSL, or similar):**
```bash
bash build.sh
```

### 3. Select "Full Setup" from the Menu

When the build script starts, you'll see an interactive menu. Choose **Option 1: Full Setup (First Time Installation)**.

This will automatically:
- ✅ Check Python installation and version
- ✅ Install all required dependencies from requirements.txt
- ✅ Create and configure the .env file
- ✅ Create required directories (uploads, profiles, tests)
- ✅ Initialize the PostgreSQL database
- ✅ Create database tables and relationships
- ✅ Seed initial data
- ✅ Prompt you to create an admin user

### Environment Variables

The build script automatically creates a `.env` file with these default settings:

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

All configuration is handled through the `.env` file that the build script creates for you.

### Database Configuration

The build script sets up the default database connection:
- **Database Name**: `blood_diagnosis_db`
- **Default User**: `postgres`
- **Default Password**: `postgres`
- **Host**: `localhost`
- **Port**: `5432`

If you need different settings, edit the `.env` file after running the build script (Option 5 in the menu).

### AI Model Configuration

The AI model files are already included in `app/ai/cbc/`:
- `tabnet_anemia_model.zip` - Trained TabNet model
- `scaler.pkl` - Feature scaler  
- `used_features.json` - Feature configuration

No additional configuration needed – the build script ensures everything is ready to use!

---

## 🗄 Database Setup

### Automatic Database Setup with Build Script

The build script handles all database operations automatically. You have several options:

### Option 1: Full Setup (Recommended for First Time)

Select **Option 1** from the build script menu. This performs complete database initialization including:
- ✅ Creating the PostgreSQL database
- ✅ Creating all tables and relationships
- ✅ Seeding initial data (AI models metadata)
- ✅ Creating an admin user account

### Option 2: Database Only

If you only need to initialize/reset the database:
1. Run the build script
2. Select **Option 7: Initialize Database**

The script will:
- ⚠️ **Warn you** that this will DROP all existing tables
- 💾 **Offer to create a backup** before proceeding
- 🔄 Recreate all tables with fresh schema
- 📊 Seed initial data

### Option 3: Create Admin User Only

If you need to create additional admin users:
1. Run the build script
2. Select **Option 8: Create Admin User**
3. Follow the interactive prompts to enter:
   - Username
   - Email
   - Password
   - First and last name
   - Other profile information

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

### Using the Build Script (Only Method)

The build script provides multiple ways to run your application:

#### Option 2: Run Application (Local Network)

**Best for development and local testing**

Select **Option 2** from the build script menu.

This will:
- ✅ Check if dependencies are installed
- ✅ Verify .env configuration exists
- ✅ Check if port 8000 is available
- ✅ Start the application with **auto-reload** (detects code changes)
- ✅ Make the app accessible on your local network

**Features:**
- 🔄 **Auto-reload**: Changes to Python files automatically restart the server
- 🌐 **Network access**: Accessible from other devices on your network
- 📝 **Live logs**: See all requests and errors in real-time
- ⚡ **Fast development**: Perfect for testing and debugging

**Access points when running:**
- Local machine: `http://localhost:8000`
- Network devices: `http://YOUR_IP:8000`
- Stop server: Press `Ctrl+C`

#### Option 3: Run Application (Public Internet via ngrok)

**Best for sharing with remote users or testing webhooks**

Select **Option 3** from the build script menu.

This will:
- ✅ Check if ngrok is installed (downloads it if needed)
- ✅ Guide you through ngrok setup (free account needed)
- ✅ Start the application on port 8000
- ✅ Create a public HTTPS tunnel using ngrok
- ✅ Display a public URL that anyone can access

**Features:**
- 🌍 **Public access**: Share your app with anyone via HTTPS URL
- 🔒 **Secure**: Automatic HTTPS encryption via ngrok
- 🚀 **No deployment needed**: Instant public access from your machine
- 📊 **ngrok dashboard**: Monitor requests via ngrok web interface

**Example ngrok output:**
```
Session Status: online
Account: Your Name (Plan: Free)
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

Share the `https://abc123.ngrok.io` URL with anyone to access your app!

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

### Running Tests with Build Script

The build script provides a comprehensive testing menu. Select **Option 11: Run Tests** from the main menu.

### Testing Options

You'll see 7 testing options:

#### 1. Run All Tests
Executes the complete test suite with verbose output.
- Tests all routes, services, and models
- Shows detailed results for each test
- Best for comprehensive validation

#### 2. Run All Tests with Coverage Report
Runs all tests and generates a detailed coverage report.
- Shows which lines of code are tested
- Generates an HTML report in `htmlcov/index.html`
- Displays coverage percentage for each file
- Helps identify untested code

**Coverage report features:**
- Line-by-line coverage visualization
- Percentage coverage per module
- Missing lines highlighted in red
- Open `htmlcov/index.html` in your browser to view

#### 3. Run Service Tests Only
Tests only the service layer (business logic).
- auth_service, patient_service, ai_service
- medical_history_service, message_service
- profile_service, policy_service, ui_service
- Faster than running all tests

#### 4. Run Route Tests Only
Tests only the API endpoints.
- Admin routes, doctor routes, patient routes
- Authentication routes, public routes
- Validates request/response handling

#### 5. Run Model/Database Tests
Tests database models and relationships.
- User model, doctor info, test results
- Medical history, messages, AI models
- Database constraints and validations

#### 6. Run Specific Test File
The script shows you all available test files and lets you choose one:

**Service Tests:**
- test_auth_service.py
- test_patient_service.py
- test_ai_service.py
- test_medical_history_service.py
- test_message_service.py
- test_profile_service.py
- test_policy_service.py
- test_ui_service.py

**Route Tests:**
- test_auth_routes.py
- test_doctor_routes.py
- test_patient_routes.py
- test_admin_routes.py
- test_public_routes.py

**Model Tests:**
- test_database_models.py

#### 7. Run Fast Tests Only
Skips slow integration tests, runs only fast unit tests.
- Perfect for quick validation during development
- Excludes database integration tests
- Completes in seconds instead of minutes

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

### Development Deployment (Using Build Script)

For development and testing, use the build script's built-in options:

#### Local Development
**Run:** Select **Option 2** from build script
- Perfect for development and testing
- Auto-reload on code changes
- Accessible on local network
- Full debugging capabilities

#### Public Testing (ngrok)
**Run:** Select **Option 3** from build script
- Instant public HTTPS URL
- Share with stakeholders for testing
- No server setup required
- Perfect for demos and feedback

### Production Deployment

#### Pre-Deployment Checklist

Before deploying to production:

1. **Update Environment Variables**
   - Use build script **Option 5** to configure `.env`
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure production database URL
   - Set up email credentials (SMTP)

2. **Database Backup**
   - The build script (**Option 7**) offers automatic backup
   - Always backup before database operations
   - Store backups securely

3. **Run Health Check**
   - Use build script **Option 10: Health Check**
   - Verifies all components are working
   - Checks database connectivity
   - Validates configuration

4. **Run Tests**
   - Use build script **Option 11: Run Tests**
   - Ensure all tests pass
   - Check test coverage is > 80%

#### Production Server Setup

For production deployment, you'll need to set up a proper web server. The build script prepares your application, but production requires:

**Recommended Stack:**
- **Application Server**: Gunicorn or Uvicorn workers
- **Reverse Proxy**: Nginx or Apache
- **Database**: PostgreSQL (managed service recommended)
- **SSL/TLS**: Let's Encrypt certificates
- **Process Manager**: systemd or supervisor

**Server Requirements:**
- Python 3.12+ installed
- PostgreSQL server running
- 2GB+ RAM (4GB+ recommended)
- 10GB+ disk space
- Ubuntu 20.04+ or similar Linux distro

#### Using Build Script for Production Setup

1. **Initial Setup on Server:**
   ```bash
   ./build.sh
   # Select Option 1: Full Setup
   ```

2. **Configure for Production:**
   ```bash
   ./build.sh
   # Select Option 5: Setup Environment Variables
   # Edit .env file with production values
   ```

3. **Verify Installation:**
   ```bash
   ./build.sh
   # Select Option 10: Health Check
   ```

4. **Run Tests:**
   ```bash
   ./build.sh
   # Select Option 11: Run Tests
   ```

After the build script completes setup, configure your production web server (Gunicorn/Nginx) according to your hosting provider's documentation.

#### Nginx Reverse Proxy Example

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
   - Fork on GitHub to your account

2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/blood-diagnosis.git
   cd blood-diagnosis
   ```

3. **Set up development environment**
   - Run `./build.sh`
   - Select **Option 1: Full Setup**
   - This ensures you have the same environment as other developers

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make your changes**
   - Write clean, documented code
   - Follow existing code patterns

6. **Test your changes**
   - Run `./build.sh`
   - Select **Option 11: Run Tests**
   - Choose **Option 2: Run all tests with coverage**
   - Ensure all tests pass and coverage stays above 80%

7. **Run health check**
   - Run `./build.sh`
   - Select **Option 10: Health Check**
   - Verify no issues before committing

8. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

9. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

10. **Create a Pull Request**
    - Go to GitHub and create a PR
    - Describe what you changed and why
    - Reference any related issues

### Development Workflow

**Daily Development:**
```bash
# Start your work session
./build.sh
# Select Option 2: Run Application (Local)

# Make changes, test automatically via auto-reload

# Before committing, run tests:
./build.sh
# Select Option 11: Run Tests
```

**Adding New Features:**
1. Discuss in GitHub issues first
2. Create feature branch
3. Use build script to set up and test
4. Submit PR with test coverage

**Fixing Bugs:**
1. Create issue describing bug
2. Create bugfix branch
3. Fix and add regression test
4. Verify with build script health check
5. Submit PR

### Code Standards

- Follow PEP 8 style guide for Python code
- Write descriptive commit messages
- Add docstrings to functions and classes
- Include type hints where applicable
- Maintain test coverage above 80%
- Use the build script for all operations

### Testing Requirements

Before submitting a PR:
- ✅ All existing tests must pass
- ✅ New features must have tests
- ✅ Bug fixes should include regression tests
- ✅ Test coverage must be ≥ 80%
- ✅ Health check must pass (Option 10)

### Reporting Issues

When reporting bugs, please include:

- Python version (from build script health check)
- Operating system
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces

---

## 🔧 Troubleshooting

### Using Build Script for Diagnostics

Before troubleshooting manually, use the build script's **Option 10: Health Check**. This will automatically:
- ✅ Verify Python installation
- ✅ Check all critical packages
- ✅ Validate .env configuration
- ✅ Test PostgreSQL connection
- ✅ Verify directory structure
- ✅ Check if application is running

The health check will pinpoint exactly what's wrong!

### Common Issues

#### 1. Database Connection Error

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 10: Health Check**
3. The script will test PostgreSQL connection
4. If connection fails, ensure PostgreSQL is installed and running
5. Use **Option 5** to verify database credentials in `.env`
6. Try **Option 7: Initialize Database** to recreate the database

**Quick Fix:**
- Ensure PostgreSQL service is running on your system
- Default credentials: `postgres` / `postgres`
- Default port: `5432`

#### 2. AI Model Not Loading

**Problem**: `Warning: Could not load CBC model`

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 10: Health Check**
3. Check if `pytorch_tabnet` is listed as installed
4. If not installed, select **Option 4: Install Dependencies**
5. This will reinstall all required packages including AI dependencies

**Note:** The application still works without AI features – only prediction functionality is disabled.

#### 3. Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'xyz'`

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 4: Install Dependencies**
3. The script will install all packages from `requirements.txt`
4. Run **Option 10: Health Check** to verify installation

#### 4. Port Already in Use

**Problem**: `[ERROR] [Errno 98] Address already in use`

**Solution:**
The build script automatically detects if port 8000 is in use and asks if you want to proceed. The running process is likely a previous instance of the application.

**To stop the previous instance:**
- Press `Ctrl+C` in the terminal running the application
- Or close the terminal window
- The build script will warn you before starting a new instance

#### 5. File Upload Issues

**Problem**: File uploads failing or not saving

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 6: Create Required Directories**
3. This recreates all upload directories with correct permissions
4. Run **Option 10: Health Check** to verify directories exist

#### 6. Configuration Issues

**Problem**: Application not starting or strange errors

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 12: Clean/Reset Everything**
3. Then select **Option 1: Full Setup**
4. This gives you a fresh installation

**Note:** Clean/Reset removes configuration but NOT the database or installed packages.

#### 7. Database Tables Missing

**Problem**: `relation "users" does not exist` or similar errors

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 7: Initialize Database**
3. The script will drop and recreate all tables
4. **Warning:** This deletes all data! The script offers to create a backup first.

#### 8. JWT Token Errors

**Problem**: `JWTError: Signature verification failed`

**Solution using Build Script:**
1. Run `./build.sh`
2. Select **Option 5: Setup Environment Variables**
3. Ensure `SECRET_KEY` in `.env` is set and consistent
4. Clear browser cookies and login again

### Complete System Reset

If you're experiencing multiple issues or want a fresh start:

1. Run `./build.sh`
2. Select **Option 12: Clean/Reset Everything** 
   - This removes configuration and cache files
3. Select **Option 1: Full Setup**
   - Complete fresh installation
4. Select **Option 10: Health Check**
   - Verify everything is working

### Build Script Menu Overview

The build script provides 12 options organized in three categories:

**QUICK START (Options 1-3):**
- **Option 1**: Full Setup - Complete first-time installation
- **Option 2**: Run Application (Local) - Start on local network
- **Option 3**: Run Application (ngrok) - Start with public URL

**SETUP & CONFIGURATION (Options 4-9):**
- **Option 4**: Install Dependencies - Install Python packages
- **Option 5**: Setup Environment - Create/update .env file
- **Option 6**: Create Directories - Make upload folders
- **Option 7**: Initialize Database - Create/reset database
- **Option 8**: Create Admin User - Add admin account
- **Option 9**: Setup ngrok - Configure public tunneling

**MAINTENANCE & TESTING (Options 10-12):**
- **Option 10**: Health Check - Diagnose system status
- **Option 11**: Run Tests - Execute test suite
- **Option 12**: Clean/Reset - Fresh start

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

## 🎯 Quick Reference

### Essential Commands

**All operations are done through the build script:**

```bash
# Start the build script
./build.sh

# Then select from the menu:
# 1 = Full Setup (first time)
# 2 = Run App (development)
# 3 = Run App (public URL)
# 10 = Health Check (troubleshooting)
# 11 = Run Tests
```

### No Manual Commands Needed!

This project is designed to be **completely managed through the build script**. You don't need to remember or run individual commands like:
- ❌ `pip install -r requirements.txt`
- ❌ `python init_db.py`
- ❌ `uvicorn app.main:app --reload`
- ❌ `pytest`

Instead, everything is accessible through the **simple menu system** in `build.sh`!

### Three Steps to Get Started

```bash
1️⃣  ./build.sh
2️⃣  Select Option 1 (Full Setup)
3️⃣  Select Option 2 (Run Application)
```

That's it! 🎉

### When You Need Help

```bash
./build.sh → Option 10: Health Check
```

This will diagnose any issues automatically!

---

<div align="center">

**Made with ❤️ for better healthcare**

⭐ Star this repository if you find it helpful!

---

### 📖 Remember: Everything through `./build.sh` - No manual commands required!

</div>

