# Public router for unauthenticated/public routes
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import get_current_user_optional
from app.models.schemas import MessageCreate
from app.services.message_service import create_message

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("public/home.html", {"request": request, "current_user": current_user})


@router.get("/about")
async def about(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("public/about.html", {"request": request, "current_user": current_user})


@router.get("/contact")
async def contact(request: Request, success: int = 0, error: int = 0, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    flash_message = None
    if success:
        flash_message = {"type": "success", "message": "Your message has been sent successfully! We'll get back to you soon."}
    elif error:
        flash_message = {"type": "error", "message": "Failed to send message. Please try again."}
    
    return templates.TemplateResponse("public/contact.html", {
        "request": request, 
        "current_user": current_user,
        "flash": flash_message
    })


@router.post("/contact")
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        message_data = MessageCreate(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        create_message(message_data, db)
        return RedirectResponse(url="/contact?success=1", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/contact?error=1", status_code=303)


@router.get("/models")
async def public_models(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.database import Model
    from sqlalchemy import func
    
    current_user = await get_current_user_optional(request, db)
    
    # Fetch actual models from database
    models = db.query(Model).all()
    
    # Calculate aggregate statistics
    total_models = len(models)
    avg_accuracy = db.query(func.avg(Model.accuracy)).scalar() or 0
    total_tests = db.query(func.sum(Model.tests_count)).scalar() or 0
    
    return templates.TemplateResponse("public/models.html", {
        "request": request,
        "current_user": current_user,
        "models": models,
        "total_models": total_models,
        "avg_accuracy": round(avg_accuracy, 2),
        "total_tests": total_tests
    })
