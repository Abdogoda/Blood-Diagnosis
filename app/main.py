from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.routers import auth, doctors, patients, admin, public
from app.services.ui_service import set_flash_message
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        from app.services.ai_service import cbc_prediction_service
        if cbc_prediction_service.is_available():
            cbc_prediction_service.load_model()
            print("✅ CBC Anemia prediction model loaded successfully")
        else:
            print("⚠️ AI prediction features disabled (missing pytorch_tabnet dependency)")
    except Exception as e:
        print(f"⚠️ Warning: Could not load CBC model: {e}")
    
    yield
    
    # Shutdown (if needed in the future)
    # Add cleanup code here

app = FastAPI(
    title=os.getenv("APP_NAME", "Blood Diagnosis System"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Blood Diagnosis System with AI-powered analysis",
    lifespan=lifespan
)

# Initialize templates early so exception handlers can use it
templates = Jinja2Templates(directory="app/templates")

# Custom exception handler for HTTP errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept_header = request.headers.get("accept", "")
    
    # Handle 401 - Unauthorized
    if exc.status_code == 401:
        if "application/json" in accept_header:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        return templates.TemplateResponse(
            "errors/401.html",
            {
                "request": request,
                "detail": exc.detail
            },
            status_code=401
        )
    
    # Handle 403 - Forbidden
    if exc.status_code == 403:
        if "application/json" in accept_header:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        
        user_role = None
        try:
            from app.services.auth_service import verify_token
            token = request.cookies.get("access_token")
            
            if token:
                if token.startswith("Bearer "):
                    token = token[7:]
                token_data = verify_token(token)
                
                if token_data and token_data.role:
                    user_role = token_data.role
        except:
            pass
        
        return templates.TemplateResponse(
            "errors/403.html",
            {
                "request": request,
                "detail": exc.detail,
                "user_role": user_role
            },
            status_code=403
        )
    
    # Handle 404 - Not Found
    if exc.status_code == 404:
        if "application/json" in accept_header:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "detail": exc.detail
            },
            status_code=404
        )
    
    # Handle other status codes with generic error page
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "error": str(exc.detail) if exc.detail else "An error occurred"
        },
        status_code=exc.status_code
    )

# Custom exception handler for 500 Internal Server Errors
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    accept_header = request.headers.get("accept", "")
    
    if "application/json" in accept_header:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred"}
        )
    
    import uuid
    error_id = str(uuid.uuid4())[:8]
    
    # Log the error (in production, you'd log to a file or monitoring service)
    print(f"Error ID {error_id}: {str(exc)}")
    
    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "detail": "An unexpected error occurred",
            "error_id": error_id
        },
        status_code=500
    )

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    accept_header = request.headers.get("accept", "")
    
    if "application/json" in accept_header:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred"}
        )
    
    import uuid
    error_id = str(uuid.uuid4())[:8]
    
    # Log the error (in production, you'd log to a file or monitoring service)
    print(f"Error ID {error_id}: {type(exc).__name__} - {str(exc)}")
    
    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "detail": "An unexpected error occurred",
            "error_id": error_id
        },
        status_code=500
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

# Include routers
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doctors.router)
app.include_router(patients.router)

