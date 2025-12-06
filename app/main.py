from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import auth, doctors, patients, files
from app.services.auth_dependencies import require_role
from app.services.flash_messages import set_flash_message
from app.database import get_db, User
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Blood Diagnosis System"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Blood Diagnosis System with AI-powered analysis"
)

# Custom exception handler for authentication errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # If it's an authentication error (401) and it's a browser request (not API)
    if exc.status_code == 401:
        # Check if it's an API request (Accept: application/json)
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header:
            # Return JSON for API requests
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        # For browser requests, redirect to login
        response = RedirectResponse(url="/auth/login", status_code=303)
        set_flash_message(response, "error", "Please login to access this page")
        return response
    
    # If it's a forbidden error (403)
    if exc.status_code == 403:
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        
        # For browser requests, try to get user role and redirect to their dashboard
        try:
            from app.services.jwt_utils import verify_token
            token = request.cookies.get("access_token")
            redirect_url = "/"
            
            if token:
                if token.startswith("Bearer "):
                    token = token[7:]
                token_data = verify_token(token)
                
                if token_data and token_data.role:
                    # Redirect based on user's role
                    if token_data.role == "admin":
                        redirect_url = "/admin/dashboard"
                    elif token_data.role == "doctor":
                        redirect_url = "/doctor/dashboard"
                    elif token_data.role == "patient":
                        redirect_url = "/patient/dashboard"
            
            response = RedirectResponse(url=redirect_url, status_code=303)
            set_flash_message(response, "error", "You don't have permission to access that page")
            return response
        except:
            # If there's any error, just redirect to home
            response = RedirectResponse(url="/", status_code=303)
            set_flash_message(response, "error", "You don't have permission to access that page")
            return response
    
    # For other HTTP exceptions, use default handling
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "error": str(exc.detail) if exc.detail else "An error occurred"
        },
        status_code=exc.status_code
    )

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(files.router)

# Public routes
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("home.html", {"request": request, "current_user": current_user})

@app.get("/about")
async def about(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("about.html", {"request": request, "current_user": current_user})

@app.get("/contact")
async def contact(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("contact.html", {"request": request, "current_user": current_user})

# Shared routes (require authentication)
@app.get("/shared/feedback")
async def feedback_page(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    if not current_user:
        response = RedirectResponse(url="/auth/login", status_code=303)
        set_flash_message(response, "error", "Please login to access feedback page")
        return response
    return templates.TemplateResponse("shared/feedback.html", {"request": request, "current_user": current_user})

@app.post("/shared/feedback")
async def submit_feedback(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # TODO: Implement feedback submission logic
    response = RedirectResponse(url=f"/{current_user.role}/dashboard", status_code=303)
    set_flash_message(response, "success", "Thank you for your feedback!")
    return response

# Admin routes
@app.get("/admin/dashboard")
def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_doctors = db.query(User).filter(User.role == "doctor").count()
    total_patients = db.query(User).filter(User.role == "patient").count()
    
    stats = {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_tests": 0,  # Will be implemented when tests are added
        "model_accuracy": 99.5,
        "avg_processing_time": 2.3
    }
    
    # Get recent users
    recent_users_query = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    recent_users = [
        {
            "initials": f"{u.fname[0]}{u.lname[0]}",
            "name": f"{u.fname} {u.lname}",
            "role": u.role.capitalize(),
            "date": u.created_at.strftime("%Y-%m-%d")
        }
        for u in recent_users_query
    ]
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "recent_users": recent_users
    })

@app.get("/admin/doctors")
def admin_doctors(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    doctors_query = db.query(User).filter(User.role == "doctor").all()
    doctors = [
        {
            "id": d.id,
            "initials": f"{d.fname[0]}{d.lname[0]}",
            "name": f"Dr. {d.fname} {d.lname}",
            "email": d.email,
            "specialization": d.doctor_info.specialization if d.doctor_info else "N/A",
            "patient_count": 0,  # Will be implemented when patient assignments are added
            "status": "active"
        }
        for d in doctors_query
    ]
    
    return templates.TemplateResponse("admin/doctors.html", {
        "request": request,
        "current_user": current_user,
        "doctors": doctors
    })

@app.get("/admin/patients")
def admin_patients(
    request: Request,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    patients_query = db.query(User).filter(User.role == "patient").all()
    patients = [
        {
            "id": p.id,
            "initials": f"{p.fname[0]}{p.lname[0]}",
            "name": f"{p.fname} {p.lname}",
            "email": p.email,
            "blood_type": p.blood_type or "N/A",
            "test_count": 0,  # Will be implemented when tests are added
            "last_visit": p.created_at.strftime("%Y-%m-%d")
        }
        for p in patients_query
    ]
    
    return templates.TemplateResponse("admin/patients.html", {
        "request": request,
        "current_user": current_user,
        "patients": patients
    })

@app.get("/admin/models")
def admin_models(
    request: Request,
    current_user: User = Depends(require_role(["admin"]))
):
    models = [
        {"name": "CBC Analysis Model", "version": "2.1", "accuracy": 99.5, "predictions": 10234, "speed": 2.1, "status": "active", "last_updated": "2025-12-01", "type": "Neural Network"},
        {"name": "Blood Image Classifier", "version": "1.8", "accuracy": 98.7, "predictions": 5000, "speed": 2.5, "status": "active", "last_updated": "2025-11-25", "type": "CNN"},
    ]
    return templates.TemplateResponse("admin/models.html", {
        "request": request,
        "current_user": current_user,
        "models": models
    })
