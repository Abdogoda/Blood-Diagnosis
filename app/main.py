from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import auth, doctors, patients, files, admin, public
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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(files.router)
