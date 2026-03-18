from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv(".env")

from routes import auth, users, menu, restock, inventory, orders, stats


#-------------------------------------
# CREATION OF THE DATABASE
# Base.metadata.create_all(bind=engine)
# -> Do not use in production
# The creation of the schema is handled by Alembic
#-------------------------------------


#-------------------------------------
# INITIALIZING THE FASTAPI APPLICATION
#-------------------------------------

tags_metadata = [
    {
        "name": "Auth",
        "description": "User signup and login (JWT-based)",
    },
    {
        "name": "User",
        "description": "User management endpoints (admin only)"
    },
    {
        "name": "Menu",
        "description": "Menu items available in the café",
    },
    {
        "name": "Inventory",
        "description": "Player inventory and stock management",
    },
    {
        "name": "Restock",
        "description": "Buy products and refill inventory",
    },
    {
        "name": "Order",
        "description": "Client orders lifecycle",
    },
    {
        "name": "Stats",
        "description": "Player and global statistics",
    }
]

app = FastAPI(
    title = "Café Manager API",
    description="Backend API for a café management game",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(menu.router)
app.include_router(restock.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(stats.router)


# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev: allow everything
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Allow all headers
)

#-------------------------------------
# HEALTH CHECK
#-------------------------------------
# @app.get("/")
# async def root():
#     """Simple homepage."""
#     return {"message": "Welcome to cafe manager"}


@app.get("/health")
async def health():
    """Check that the application is working."""
    return {"status": "ok"}