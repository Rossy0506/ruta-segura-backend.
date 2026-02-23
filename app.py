import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

# 1. Configuración de Firebase
# Asegúrate de que el archivo se llame exactamente LLAVE.json en tu carpeta
cred = credentials.Certificate("LLAVE.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# 2. SOLUCIÓN AL ERROR DE CONEXIÓN (CORS)
# Esto permite que tu index.html se comunique con Render sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Modelos de datos
class Alerta(BaseModel):
    lat: float
    lng: float
    tipo: str
    usuario: str

# 4. RUTAS DEL SERVIDOR

@app.get("/")
def inicio():
    return {"message": "Servidor de Ruta Segura Funcionando"}

@app.post("/reportar")
async def reportar_incidente(alerta: Alerta):
    try:
        # Guarda la alerta en Firebase
        doc_ref = db.collection("alertas").document()
        doc_ref.set(alerta.dict())
        return {"status": "ok", "id": doc_ref.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/alertas", response_model=List[Alerta])
async def obtener_alertas():
    alertas = []
    try:
        docs = db.collection("alertas").stream()
        for doc in docs:
            alertas.append(doc.to_dict())
    except Exception as e:
        print(f"Error al obtener alertas: {e}")
    return alertas

# 5. Configuración para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)