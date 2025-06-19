from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import Item as DBItem
from database import SessionLocal, engine, Base

app = FastAPI()

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Esquema Pydantic
class ItemResponse(BaseModel):
    id: int
    pais: str
    codigo: str

    class Config:
        orm_mode = True

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/paises", response_model=List[ItemResponse])
def get_paises(db: Session = Depends(get_db)):
    return db.query(DBItem).all()
