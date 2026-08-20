from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from config.database import get_db

router = APIRouter(prefix="/api/licitaciones", tags=["Licitaciones"])
db = get_db()

@router.get("/")
def listar_licitaciones(
    empresa: Optional[str] = Query(None, description="Filtro: coimsa, induwork, especial"),
    tipo: Optional[str] = Query(None, description="Filtro: Licitación, Compra Ágil"),
    limit: int = 20,
    skip: int = 0
):
    if db is None:
        raise HTTPException(status_code=500, detail="Sin conexión a la base de datos")

    query = {}
    if empresa:
        query[f"clasificacion.{empresa}"] = True
    if tipo:
        query["tipo"] = tipo

    total = db["licitaciones"].count_documents(query)
    cursor = db["licitaciones"].find(query, {"_id": 0}).sort("fecha_captura", -1).skip(skip).limit(limit)
    
    return {
        "total": total,
        "items": list(cursor)
    }

@router.get("/{id_licitacion}")
def obtener_detalle_licitacion(id_licitacion: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Sin conexión a la base de datos")

    licitacion = db["licitaciones"].find_one({"id": id_licitacion}, {"_id": 0})
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    return licitacion