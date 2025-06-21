from fastapi import FastAPI, Depends,Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List,Optional
from models import Item as DBItem
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Peligroso en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
def get_paises(limit: Optional[int] = Query(None,gt=0), db: Session = Depends(get_db)):
        result=db.query(DBItem).order_by(DBItem.id.asc())
        if limit:
            result=result.limit(limit)
        return result.all()
