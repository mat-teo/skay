from fastapi import FastAPI, Request
from rate_limit import setup_rate_limiting, limiter
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
from routers import categories, users, accounts, transactions, auth, health, budgets
from logger import setup_logger
from rate_limit import limiter, TESTING

logger = setup_logger(__name__)

app = FastAPI(title="Skay Finance API", version="0.7")

setup_rate_limiting(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", 
                   "http://127.0.0.1:5173",
                    "http://localhost",         
                    "http://127.0.0.1",
                    "http://localhost:8000",],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    logger.info("Starting skay API...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down skay API")

# Include professional modular routers
app.include_router(users.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(health.router,prefix="/api")
app.include_router(budgets.router,prefix="/api")

if not TESTING:
    for route in auth.router.routes:
        if route.path == "/login":
            route.endpoint = limiter.limit("5/minute")(route.endpoint)
        elif route.path == "/register":
            route.endpoint = limiter.limit("3/minute")(route.endpoint)

@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    return {"message": "Skay API is running"}