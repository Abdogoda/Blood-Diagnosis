# Public router for unauthenticated/public routes
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import get_current_user_optional

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
async def contact(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("public/contact.html", {"request": request, "current_user": current_user})


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
