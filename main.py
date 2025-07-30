from fastapi import FastAPI, Depends,Query,HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List,Optional
from models import Item as DBItem
from models import Personas
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from decimal import Decimal
import base64
from io import BytesIO
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
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
class DecryptRequest(BaseModel):
    media_key_b64: str
    encrypted_url: str
# Esquema Pydantic
class ItemResponse(BaseModel):
    id: int
    pais: str
    codigo: str

    class Config:
        orm_mode = True
class PersonasResponse(BaseModel):
    id : int
    telefono : str
    empresa : str
    personas: Optional[str] = None
    id_ubigeo: Optional[int] = None
    fecha: Optional[datetime] = None
    monto: Optional[Decimal] = None
    ruc: Optional[str] = None
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
@app.get("/personas",response_model=List[PersonasResponse])
def get_personas(db: Session = Depends(get_db)):
        result=db.query(Personas).order_by(Personas.id.asc())
        return result.all()
@app.post("/decrypt_audio")
def decrypt_audio(data: DecryptRequest):
    try:
        # Descargar archivo cifrado
        res = requests.get(data.encrypted_url)
        res.raise_for_status()
        encrypted_data = res.content

        # Decodificar mediaKey y derivar claves
        media_key = base64.b64decode(data.media_key_b64)
        info = b"WhatsApp Audio Keys"

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=112,
            salt=None,
            info=info,
            backend=default_backend()
        )
        derived = hkdf.derive(media_key)

        iv = derived[0:16]
        cipher_key = derived[16:48]

        # Remover MAC de 10 bytes del final
        encrypted_data = encrypted_data[:-10]

        # Desencriptar AES-CBC
        cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)

        # Quitar padding PKCS#7
        decrypted_data = unpad(decrypted_data, AES.block_size)

        # Devolver el archivo desencriptado como stream (audio .ogg u otro)
        return StreamingResponse(BytesIO(decrypted_data), media_type="audio/ogg")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al desencriptar: {str(e)}")
