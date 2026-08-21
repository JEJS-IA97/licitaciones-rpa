from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from zoneinfo import ZoneInfo
from datetime import datetime

from config.database import get_db
from config.settings import CORS_ORIGINS
from api.endpoints import licitaciones, documentos, automatizacion # <-- Agrega automatizacion

app = FastAPI(
    title="Bot Mercado Público RPA & AI",
    description="API para gestión, análisis e interacción automatizada con licitaciones.",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(licitaciones.router)
app.include_router(documentos.router)
app.include_router(automatizacion.router) # <-- Registra el router de Playwright

CL_TZ = ZoneInfo("America/Santiago")

@app.get("/")
def estado_bot():
    return {
        "status": "online",
        "sistema": "RPA Mercado Público API",
        "hora_chile": datetime.now(CL_TZ).isoformat()
    }