from sqlalchemy import Column, Integer, String, Float, DateTime, Numeric
from database import Base
from datetime import datetime

class Item(Base):
    __tablename__ = "codigo_pais"

    id = Column(Integer, primary_key=True, index=True)
    pais = Column(String, index=True)
    codigo = Column(String, index=True)
class Personas(Base):
    __tablename__="personas"

    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String, index=True)
    empresa = Column(String, index=True)
    persona = Column(String, index=True)
    id_ubigeo = Column(Integer, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)  # Tipo timestamp
    monto = Column(Numeric(10, 2), index=True)
    ruc = Column(String, index=True)
