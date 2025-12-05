from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import auth, doctors, patients, files

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(files.router)

# Public routes
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# Admin routes
@app.get("/admin/dashboard")
def admin_dashboard(request: Request):
    stats = {
        "total_users": 1234,
        "total_tests": 5678,
        "model_accuracy": 99.5,
        "avg_processing_time": 2.3
    }
    recent_users = [
        {"initials": "JD", "name": "Dr. John Doe", "role": "Doctor", "date": "2025-12-05"},
        {"initials": "SM", "name": "Sarah Miller", "role": "Patient", "date": "2025-12-04"},
    ]
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_users": recent_users
    })

@app.get("/admin/doctors")
def admin_doctors(request: Request):
    doctors = [
        {"initials": "JD", "name": "Dr. John Doe", "email": "john@example.com", "specialization": "Hematology", "patient_count": 45, "status": "active"},
        {"initials": "ES", "name": "Dr. Emily Smith", "email": "emily@example.com", "specialization": "Pathology", "patient_count": 38, "status": "active"},
    ]
    return templates.TemplateResponse("admin/doctors.html", {"request": request, "doctors": doctors})

@app.get("/admin/patients")
def admin_patients(request: Request):
    patients = [
        {"initials": "SM", "name": "Sarah Miller", "email": "sarah@example.com", "age": 32, "test_count": 5, "last_visit": "2025-12-01"},
        {"initials": "MJ", "name": "Michael Johnson", "email": "michael@example.com", "age": 45, "test_count": 8, "last_visit": "2025-11-28"},
    ]
    return templates.TemplateResponse("admin/patients.html", {"request": request, "patients": patients})

@app.get("/admin/models")
def admin_models(request: Request):
    models = [
        {"name": "CBC Analysis Model", "version": "2.1", "accuracy": 99.5, "predictions": 10234, "speed": 2.1, "status": "active", "last_updated": "2025-12-01", "type": "Neural Network"},
        {"name": "Blood Image Classifier", "version": "1.8", "accuracy": 98.7, "predictions": 5000, "speed": 2.5, "status": "active", "last_updated": "2025-11-25", "type": "CNN"},
    ]
    return templates.TemplateResponse("admin/models.html", {"request": request, "models": models})
