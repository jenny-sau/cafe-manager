from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal

from database import get_db
import models
from auth import verify_password, create_access_token, decode_access_token, hash_password

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


# ==========================================
# ROUTES INTERFACE WEB
# ==========================================
@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/bar")
def bar(request: Request):
    return templates.TemplateResponse("bar.html", {"request": request})

@router.get("/kitchen")
def kitchen(request: Request):
    return templates.TemplateResponse("kitchen.html", {"request": request})

@router.get("/drive")
def kitchen(request: Request):
    return templates.TemplateResponse("drive.html", {"request": request})


# @router.get("/", response_class=HTMLResponse, include_in_schema=False)
# async def home(request: Request):
#     """Home page."""
#
#
#
# @router.get("/signup", response_class=HTMLResponse, include_in_schema=False)
# async def signup_page(request: Request):
#     """Registration page."""
#     return templates.TemplateResponse("signup.html", {"request": request})
#
#
# @router.post("/signup", response_class=HTMLResponse, include_in_schema=False)
# async def signup_form(
#         request: Request,
#         username: str = Form(...),
#         password: str = Form(...),
#         money: Decimal = Form(Decimal("1000.00")),
#         db: Session = Depends(get_db)
# ):
#     """Process the registration form."""
#     existing_user = db.query(models.User).filter(
#         models.User.username == username
#     ).first()
#
#     if existing_user:
#         return templates.TemplateResponse(
#             "signup.html",
#             {"request": request, "error": "Ce nom d'utilisateur existe déjà"}
#         )
#
#     hashed = hash_password(password)
#     db_user = models.User(
#         username=username,
#         password_hash=hashed,
#         money=money,
#         is_admin=False
#     )
#
#     db.add(db_user)
#     db.commit()
#
#     return RedirectResponse(url="/login?success=1", status_code=303)
#
#
# @router.get("/login", response_class=HTMLResponse, include_in_schema=False)
# async def login_page(request: Request, success: int = 0):
#     """Login page."""
#     success_msg = "Compte créé avec succès ! Vous pouvez vous connecter." if success else None
#     return templates.TemplateResponse(
#         "login.html",
#         {"request": request, "success": success_msg}
#     )
#
#
# @router.post("/login", response_class=HTMLResponse, include_in_schema=False)
# async def login_form(
#         request: Request,
#         username: str = Form(...),
#         password: str = Form(...),
#         db: Session = Depends(get_db)
# ):
#     """Process the login form."""
#     user = db.query(models.User).filter(
#         models.User.username == username
#     ).first()
#
#     if not user or not verify_password(password, user.password_hash):
#         return templates.TemplateResponse(
#             "login.html",
#             {"request": request, "error": "Nom d'utilisateur ou mot de passe incorrect"}
#         )
#
#     access_token = create_access_token(data={"user_id": user.id})
#
#     response = RedirectResponse(url="/bar", status_code=303)
#     response.set_cookie(key="access_token", value=access_token, httponly=True)
#     return response
#
# @router.get("/bar")
# def bar (request: Request)
#     return templates.TemplateResponse("bar.html", {"request": request})
#
#
# @router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
# async def dashboard(request: Request, db: Session = Depends(get_db)):
#     """Player dashboard page."""
#     token = request.cookies.get("access_token")
#
#     if not token:
#         return RedirectResponse(url="/login", status_code=303)
#
#     try:
#         payload = decode_access_token(token)
#         user_id = payload["user_id"]
#
#         user = db.query(models.User).filter(models.User.id == user_id).first()
#
#         if not user:
#             return RedirectResponse(url="/login", status_code=303)
#
#         progress = db.query(models.PlayerProgress).filter(
#             models.PlayerProgress.user_id == user.id
#         ).first()
#
#         if not progress:
#             progress = models.PlayerProgress(
#                 user_id=user.id,
#                 total_money_earned=Decimal("0.00"),
#                 total_orders=0,
#                 current_level=1,
#                 total_money_spent=Decimal("0.00")
#             )
#             db.add(progress)
#             db.commit()
#             db.refresh(progress)
#
#         level_requirements = {
#             1: {"money": 100, "orders": 10},
#             2: {"money": 500, "orders": 50},
#             3: {"money": 2000, "orders": 200},
#             4: {"money": 10000, "orders": 1000},
#         }
#
#         next_level = progress.current_level + 1 if progress.current_level < 5 else 5
#         next_requirements = level_requirements.get(progress.current_level, {"money": 10000, "orders": 1000})
#
#         money_percent = min(100, (progress.total_money_earned / next_requirements["money"]) * 100)
#         orders_percent = min(100, (progress.total_orders / next_requirements["orders"]) * 100)
#
#         can_level_up = (progress.total_money_earned >= next_requirements["money"] and
#                         progress.total_orders >= next_requirements["orders"])
#
#         notifications = []
#
#         inventory = db.query(models.Inventory).filter(
#             models.Inventory.user_id == user.id,
#             models.Inventory.quantity < 10
#         ).all()
#
#         for inv in inventory:
#             menu_item = db.query(models.MenuItem).filter(
#                 models.MenuItem.id == inv.menu_item_id
#             ).first()
#             if menu_item:
#                 notifications.append({
#                     "type": "warning",
#                     "message": f" Stock faible : {menu_item.name} ({inv.quantity} unités)"
#                 })
#
#         return templates.TemplateResponse("dashboard.html", {
#             "request": request,
#             "player": {
#                 "username": user.username,
#                 "money": round(user.money, 2),
#                 "level": progress.current_level
#             },
#             "progress": {
#                 "earned": round(progress.total_money_earned, 2),
#                 "orders": progress.total_orders,
#                 "next_level_money": next_requirements["money"],
#                 "next_level_orders": next_requirements["orders"],
#                 "money_percent": round(money_percent, 2),
#                 "orders_percent": round(orders_percent, 2),
#                 "can_level_up": can_level_up
#             },
#             "notifications": notifications
#         })
#
#     except Exception as e:
#         print(f"Erreur dashboard: {e}")
#         return RedirectResponse(url="/login", status_code=303)
#
#
# @router.get("/logout", include_in_schema=False)
# async def logout():
#     """Log out."""
#     response = RedirectResponse(url="/", status_code=303)
#     response.delete_cookie("access_token")
#     return response
#
#
# @router.get("/stock", response_class=HTMLResponse, include_in_schema=False)
# async def stock(request: Request, db: Session = Depends(get_db)):
#     """Stock management page."""
#     token = request.cookies.get("access_token")
#
#     if not token:
#         return RedirectResponse(url="/login", status_code=303)
#
#     try:
#         # Décoder le token
#         payload = decode_access_token(token)
#         user_id = payload["user_id"]
#
#         # Récupérer le user
#         user = db.query(models.User).filter(models.User.id == user_id).first()
#
#         if not user:
#             return RedirectResponse(url="/login", status_code=303)
#
#         # Récupérer l'inventaire
#         inventory = db.query(models.Inventory).filter(
#             models.Inventory.user_id == user.id
#         ).all()
#
#         # Enrichir avec les détails du menu
#         stock_items = []
#         for inv in inventory:
#             menu_item = db.query(models.MenuItem).filter(
#                 models.MenuItem.id == inv.menu_item_id
#             ).first()
#
#             if menu_item:
#                 stock_items.append({
#                     "id": inv.id,
#                     "menu_item_id": inv.menu_item_id,
#                     "name": menu_item.name,
#                     "quantity": inv.quantity,
#                     "status": "low" if inv.quantity < 10 else "ok"
#                 })
#
#         return templates.TemplateResponse("stock.html", {
#             "request": request,
#             "player": {
#                 "username": user.username,
#                 "money": round(user.money, 2)
#             },
#             "stock_items": stock_items
#         })
#
#     except Exception as e:
#         print(f"Erreur stock: {e}")
#         return RedirectResponse(url="/login", status_code=303)
#
#
# @router.get("/stats", response_class=HTMLResponse, include_in_schema=False)
# async def stats(request: Request, db: Session = Depends(get_db)):
#     """Page stats"""
#     token = request.cookies.get("access_token")
#
#     if not token:
#         return RedirectResponse(url="/login", status_code=303)
#
#     try:
#         # Décoder le token
#         payload = decode_access_token(token)
#         user_id = payload["user_id"]
#
#         # Récupérer le user
#         user = db.query(models.User).filter(models.User.id == user_id).first()
#
#         if not user:
#             return RedirectResponse(url="/login", status_code=303)
#
#         # Récupérer les stats
#         progress = db.query(models.PlayerProgress).filter(
#             models.PlayerProgress.user_id == user.id
#         ).first()
#
#         if not progress:
#             progress = models.PlayerProgress(
#                 user_id=user.id,
#                 total_money_earned=Decimal("0.00"),
#                 total_orders=0,
#                 current_level=1,
#                 total_money_spent=Decimal("0.00")
#             )
#             db.add(progress)
#             db.commit()
#             db.refresh(progress)
#
#         # Calculer le profit
#         profit = progress.total_money_earned - progress.total_money_spent
#
#         return templates.TemplateResponse("stats.html", {
#             "request": request,
#             "player": {
#                 "username": user.username,
#                 "money": round(user.money, 2),
#                 "level": progress.current_level
#             },
#             "stats": {
#                 "total_earned": round(progress.total_money_earned, 2),
#                 "total_spent": round(progress.total_money_spent, 2),
#                 "profit": round(profit, 2),
#                 "total_orders": progress.total_orders
#             }
#         })
#
#     except Exception as e:
#         print(f"Erreur stats: {e}")
#         return RedirectResponse(url="/login", status_code=303)