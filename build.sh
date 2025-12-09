#!/bin/bash
# Blood Diagnosis System - Interactive Build Script
# Uses system Python 3.12 directly

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${CYAN}================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check Python installation
check_python() {
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        print_error "Python is not installed!"
        echo "Please install Python 3.12"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Using system Python $PYTHON_VERSION"
}

# 1. Install Dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    print_info "Upgrading pip, setuptools, and wheel..."
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel 2>/dev/null || print_warning "Pip upgrade skipped"
    
    print_info "Installing requirements from requirements.txt..."
    print_warning "This may take a few minutes, especially for packages like numpy, opencv, pytorch-tabnet, etc..."
    
    $PYTHON_CMD -m pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        echo ""
        print_warning "Check the error message above for details."
        return 1
    fi
}

# 2. Setup Environment Variables
setup_env() {
    print_header "Setting Up Environment Variables"
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? [Y/n]: " -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_info "Keeping existing .env file"
            return 0
        fi
    fi
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
    else
        cat > .env << 'EOF'
# Blood Diagnosis System Environment Variables
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/blood_diagnosis_db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Blood Diagnosis System
APP_VERSION=1.0.0
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
EOF
        print_success "Created .env file with default values"
    fi
    
    print_warning "Please update .env file with your configuration"
}

# 3. Create Directories
create_directories() {
    print_header "Creating Required Directories"
    
    mkdir -p uploads/profiles
    mkdir -p uploads/tests
    
    print_success "Created uploads/profiles"
    print_success "Created uploads/tests"
}

# 4. Initialize Database
init_database() {
    print_header "Initializing Database"
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        echo "Please setup environment variables first (Option 2)"
        return 1
    fi
    
    print_warning "This will DROP all existing tables and recreate them!"
    echo "  Database: blood_diagnosis_db"
    echo "  User: postgres (or as configured in .env)"
    echo ""
    echo "⚠️  WARNING: ALL DATA WILL BE LOST!"
    echo ""
    echo "To create database manually, run:"
    echo "  psql -U postgres -c 'CREATE DATABASE blood_diagnosis_db;'"
    echo ""
    read -p "Continue? [Y/n]: " -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Database initialization cancelled"
        return 0
    fi
    
    print_info "Dropping and recreating database tables..."
    $PYTHON_CMD init_db.py
    
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
    else
        print_error "Failed to initialize database"
        return 1
    fi
}

# 5. Create Admin User
create_admin() {
    print_header "Creating Admin User"
    
    print_info "Starting admin creation script..."
    $PYTHON_CMD create_admin.py
}

# 6. Run Application
run_app() {
    print_header "Starting Blood Diagnosis System"
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        echo "Please setup environment variables first (Option 2)"
        return 1
    fi
    
    # Check if uvicorn is installed
    if ! $PYTHON_CMD -c "import uvicorn" 2>/dev/null; then
        print_error "uvicorn not installed!"
        echo "Please install dependencies first (Option 1)"
        return 1
    fi
    
    print_info "Application will be available at: http://localhost:8000"
    print_info "Press CTRL+C to stop"
    echo ""
    
    $PYTHON_CMD -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# 7. Full Setup
full_setup() {
    print_header "FULL SETUP - All Steps"
    
    echo "This will perform all setup steps:"
    echo "  1. Install dependencies"
    echo "  2. Setup environment variables"
    echo "  3. Create directories"
    echo "  4. Initialize database (drop & recreate)"
    echo "  5. Create admin user"
    echo ""
    read -p "Continue with full setup? [Y/n]: " -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Full setup cancelled"
        return 0
    fi
    
    install_dependencies
    setup_env
    create_directories
    init_database
    
    echo ""
    read -p "Do you want to create an admin user now? [Y/n]: " -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        create_admin
    fi
    
    print_header "SETUP COMPLETED!"
    echo "To start the application, run: ./build.sh and select option 6"
    echo "Or run manually: python -m uvicorn app.main:app --reload"
}

# 8. Clean/Reset
clean_reset() {
    print_header "Clean/Reset Environment"
    
    echo "This will remove:"
    echo "  - Environment file (.env)"
    echo "  - Upload directories (uploads/)"
    echo "  - Python cache files (__pycache__)"
    echo ""
    print_warning "This will NOT delete the database or uninstall packages!"
    echo ""
    read -p "Are you sure you want to continue? [Y/n]: " -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Clean cancelled"
        return 0
    fi
    
    print_info "Removing .env file..."
    rm -f .env
    
    print_info "Removing upload directories..."
    rm -rf uploads
    
    print_info "Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Clean completed!"
    echo "Run full setup (option 7) to start fresh"
}

# 9. Setup ngrok
setup_ngrok() {
    print_header "Setup ngrok (Public URL Tunnel)"
    
    # Check if ngrok already exists
    if [ -f "./ngrok.exe" ] || command -v ngrok &> /dev/null; then
        print_success "ngrok is already installed"
        
        # Check if authtoken is configured
        if [ -f "$HOME/.ngrok2/ngrok.yml" ] || [ -f "$USERPROFILE/.ngrok2/ngrok.yml" ]; then
            print_success "ngrok authtoken is configured"
            return 0
        fi
    else
        print_info "Downloading ngrok for Windows..."
        
        # Download ngrok for Windows
        curl -L "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -o ngrok.zip
        
        if [ $? -eq 0 ]; then
            print_info "Extracting ngrok..."
            unzip -o ngrok.zip
            rm ngrok.zip
            print_success "ngrok downloaded successfully"
        else
            print_error "Failed to download ngrok"
            echo "Please download manually from: https://ngrok.com/download"
            return 1
        fi
    fi
    
    # Configure authtoken
    echo ""
    print_info "To use ngrok, you need a free authtoken from ngrok.com"
    echo ""
    echo "Steps:"
    echo "  1. Go to https://dashboard.ngrok.com/signup (free account)"
    echo "  2. After login, go to: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "  3. Copy your authtoken"
    echo ""
    read -p "Do you have an ngrok authtoken? [Y/n]: " -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        read -p "Enter your ngrok authtoken: " authtoken
        
        if [ ! -z "$authtoken" ]; then
            if [ -f "./ngrok.exe" ]; then
                ./ngrok.exe config add-authtoken "$authtoken"
            else
                ngrok config add-authtoken "$authtoken"
            fi
            
            if [ $? -eq 0 ]; then
                print_success "ngrok authtoken configured successfully!"
            else
                print_error "Failed to configure authtoken"
                return 1
            fi
        fi
    else
        print_warning "You can configure the authtoken later with:"
        echo "  ./ngrok.exe config add-authtoken YOUR_TOKEN"
    fi
}

# 10. Run with ngrok
run_with_ngrok() {
    print_header "Running Application with ngrok Tunnel"
    
    # Check if ngrok exists
    if [ ! -f "./ngrok.exe" ] && ! command -v ngrok &> /dev/null; then
        print_error "ngrok is not installed!"
        echo ""
        read -p "Do you want to setup ngrok now? [Y/n]: " -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            setup_ngrok
            if [ $? -ne 0 ]; then
                return 1
            fi
        else
            return 1
        fi
    fi
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        echo "Please setup environment variables first (Option 2)"
        return 1
    fi
    
    # Check if uvicorn is installed
    if ! $PYTHON_CMD -c "import uvicorn" 2>/dev/null; then
        print_error "uvicorn not installed!"
        echo "Please install dependencies first (Option 1)"
        return 1
    fi
    
    print_info "Starting application on port 8000..."
    print_info "Starting ngrok tunnel..."
    echo ""
    
    # Start uvicorn in background
    $PYTHON_CMD -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    UVICORN_PID=$!
    
    # Wait a bit for server to start
    sleep 3
    
    # Start ngrok
    if [ -f "./ngrok.exe" ]; then
        ./ngrok.exe http 8000
    else
        ngrok http 8000
    fi
    
    # When ngrok is closed, kill uvicorn
    print_info "Stopping application..."
    kill $UVICORN_PID 2>/dev/null
}

# 11. Run Tests
run_tests() {
    print_header "Running Test Suite"
    
    echo "Test Options:"
    echo "  1) Run all tests"
    echo "  2) Run all tests with coverage report"
    echo "  3) Run service tests only"
    echo "  4) Run route tests only"
    echo "  5) Run model/database tests"
    echo "  6) Run specific test file"
    echo "  7) Run fast tests (skip slow/integration)"
    echo ""
    read -p "Select test option [1-7]: " test_choice
    
    case $test_choice in
        1)
            print_info "Running all tests..."
            $PYTHON_CMD -m pytest tests/ -v --tb=short
            ;;
        2)
            print_info "Running all tests with coverage..."
            $PYTHON_CMD -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
            print_success "Coverage report generated in htmlcov/index.html"
            ;;
        3)
            print_info "Running service tests only..."
            $PYTHON_CMD -m pytest tests/ -k "service" -v --tb=short
            ;;
        4)
            print_info "Running route tests only..."
            $PYTHON_CMD -m pytest tests/ -k "routes" -v --tb=short
            ;;
        5)
            print_info "Running model and database tests..."
            $PYTHON_CMD -m pytest tests/test_database_models.py -v --tb=short
            ;;
        6)
            echo ""
            echo "Available test files:"
            echo "  Service Tests:"
            echo "    - test_auth_service.py"
            echo "    - test_patient_service.py"
            echo "    - test_ai_service.py"
            echo "    - test_ui_service.py"
            echo "    - test_medical_history_service.py"
            echo "    - test_message_service.py"
            echo "    - test_profile_service.py"
            echo "    - test_policy_service.py"
            echo ""
            echo "  Route Tests:"
            echo "    - test_auth_routes.py"
            echo "    - test_doctor_routes.py"
            echo "    - test_patient_routes.py"
            echo "    - test_admin_routes.py"
            echo "    - test_public_routes.py"
            echo ""
            echo "  Model Tests:"
            echo "    - test_database_models.py"
            echo ""
            read -p "Enter test file name: " test_file
            print_info "Running tests/$test_file..."
            $PYTHON_CMD -m pytest tests/$test_file -v --tb=short
            ;;
        7)
            print_info "Running fast tests only (excluding slow/integration tests)..."
            $PYTHON_CMD -m pytest tests/ -v --tb=short -m "not slow and not integration"
            ;;
        *)
            print_error "Invalid option"
            return 1
            ;;
    esac
    
    echo ""
    print_success "Test execution completed!"
}

# Main Menu
show_menu() {
    clear
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}       BLOOD DIAGNOSIS SYSTEM - BUILD & DEPLOY TOOL${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo ""
    echo -e "${YELLOW}QUICK START:${NC}"
    echo "   1) Full Setup (First Time Installation)"
    echo "   2) Run Application (Local Network)"
    echo "   3) Run Application (Public Internet via ngrok)"
    echo ""
    echo -e "${YELLOW}SETUP & CONFIGURATION:${NC}"
    echo "   4) Install Dependencies"
    echo "   5) Setup Environment Variables"
    echo "   6) Create Required Directories"
    echo "   7) Initialize Database (Drop & Recreate)"
    echo "   8) Create Admin User"
    echo "   9) Setup ngrok (For Public Access)"
    echo ""
    echo -e "${YELLOW}MAINTENANCE & TESTING:${NC}"
    echo "  10) Run Tests"
    echo "  11) Clean/Reset Everything"
    echo ""
    echo "   0) Exit"
    echo ""
    echo -e "${CYAN}================================================================${NC}"
}

# Main execution
main() {
    check_python
    
    while true; do
        show_menu
        read -p "Enter your choice [0-11]: " choice
        
        case $choice in
            1) full_setup ;;
            2) run_app ;;
            3) run_with_ngrok ;;
            4) install_dependencies ;;
            5) setup_env ;;
            6) create_directories ;;
            7) init_database ;;
            8) create_admin ;;
            9) setup_ngrok ;;
            10) run_tests ;;
            11) clean_reset ;;
            0) 
                echo ""
                print_success "Goodbye!"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 0-11"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
