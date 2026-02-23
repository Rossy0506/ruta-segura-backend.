from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

# Esto le dice al navegador: "Confía en cualquier origen"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verifica que el nombre del archivo sea igual al que tienes en la carpeta
cred = credentials.Certificate("LLAVE.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

@app.post("/reportar")
async def reportar(datos: dict):
    print(f"Recibido: {datos}") # Esto imprimirá el reporte en tu terminal negra
    db.collection("operativos").add(datos)
    return {"status": "ok"}