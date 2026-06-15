from sqlmodel import create_engine, Session, SQLModel
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skay.db")
if "pytest" in sys.modules:
    DATABASE_URL = "sqlite:///./test.db"
    
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, echo=False)
else:
    engine = create_engine(DATABASE_URL, echo=True)



def get_db():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)