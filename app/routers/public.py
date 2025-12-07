# Public router for unauthenticated/public routes
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("home.html", {"request": request, "current_user": current_user})


@router.get("/about")
async def about(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("about.html", {"request": request, "current_user": current_user})


@router.get("/contact")
async def contact(request: Request, db: Session = Depends(get_db)):
    from app.services.auth_dependencies import get_current_user_optional
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse("contact.html", {"request": request, "current_user": current_user})
