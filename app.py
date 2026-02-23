import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn

# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("LLAVE.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Reporte(BaseModel):
    lat: float
    lng: float
    tipo: str  # Municipalidad, Policía, Sutran
    usuario_alias: str
    foto_url: Optional[str] = ""
    hora: str

@app.post("/reportar")
async def reportar_operativo(data: Reporte):
    try:
        # Añadimos la hora del servidor para calcular la expiración luego
        reporte_dict = data.dict()
        reporte_dict["timestamp"] = datetime.now()
        db.collection("operativos_viales").add(reporte_dict)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/alertas", response_model=List[Reporte])
async def obtener_operativos():
    lista = []
    # Solo traer operativos de las últimas 2 horas
    hace_dos_horas = datetime.now() - timedelta(hours=2)
    
    docs = db.collection("operativos_viales")\
             .where("timestamp", ">", hace_dos_horas)\
             .stream()
    
    for doc in docs:
        lista.append(doc.to_dict())
    return lista

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    