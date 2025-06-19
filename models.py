from sqlalchemy import Column, Integer, String, Float
from database import Base

class Item(Base):
    __tablename__ = "codigo_pais"

    id = Column(Integer, primary_key=True, index=True)
    pais = Column(String, index=True)
    codigo = Column(String, index=True)
