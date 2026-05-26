from typing import Optional, List
from fastapi import FastAPI
from sqlmodel import Field, SQLModel, create_engine, Session, select

# 1. Definizione del modello del Database (Questo genera sia il DB che la documentazione)
class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str        # Es. "Contanti", "Banca 1"
    type: str        # Es. "cash", "bank"
    balance: float   # Saldo attuale

# 2. Configurazione del Database (Inizialmente usiamo SQLite per semplicità, poi lo colleghiamo a Postgres)
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

# 3. Inizializzazione FastAPI
app = FastAPI(title="Skay API", version="0.1")

# Crea le tabelle all'avvio dell'applicazione
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# 4. Endpoint API (Rotte)
@app.get("/accounts", response_model=List[Account], tags=["Accounts"])
def get_accounts():
    """Get all accounts (e.g., Banks, Cash)"""
    with Session(engine) as session:
        accounts = session.exec(select(Account)).all()
        return accounts

@app.post("/accounts", response_model=Account, tags=["Accounts"])
def create_account(account: Account):
    """Create a new account (e.g., Bank, Cash)"""
    with Session(engine) as session:
        session.add(account)
        session.commit()
        session.refresh(account)
        return account