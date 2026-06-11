from fastapi import FastAPI, Request
from rate_limit import setup_rate_limiting, limiter
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
from routers import categories, users, accounts, transactions, auth

app = FastAPI(title="Skay Finance API", version="0.7")

setup_rate_limiting(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Include professional modular routers
app.include_router(users.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")


@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    return {"message": "Skay API is running"}