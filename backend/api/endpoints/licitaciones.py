import requests
from fastapi import APIRouter, HTTPException
from config.database import get_db
from config.settings import CHILECOMPRA_TICKET

router = APIRouter(prefix="/api/licitaciones", tags=["Licitaciones"])

@router.get("/")
def listar_licitaciones():
    """Obtiene todas las licitaciones guardadas en MongoDB."""
    db = get_db()
    licitaciones = list(db.licitaciones.find({}, {"_id": 0}))
    return licitaciones

@router.post("/sincronizar")
def sincronizar_licitaciones_activas():
    """
    Consulta la API oficial de Mercado Público para traer las licitaciones
    activas del día y las guarda o actualiza en MongoDB.
    """
    if not CHILECOMPRA_TICKET:
        raise HTTPException(
            status_code=400, 
            detail="Falta el CHILECOMPRA_TICKET en el archivo .env"
        )

    db = get_db()
    
    # Elimina el índice único en 'id' si existe para evitar bloqueos por id: null
    try:
        db.licitaciones.drop_index("id_1")
    except Exception:
        pass

    url_api = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=activas&ticket={CHILECOMPRA_TICKET}"

    try:
        response = requests.get(url_api, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        listado = data.get("Listado", [])
        if not listado:
            return {
                "status": "ok", 
                "mensaje": "No se encontraron licitaciones activas en este momento.", 
                "guardados_en_db": 0
            }

        procesados = 0

        for item in listado:
            codigo = item.get("CodigoExterno")
            if codigo:
                # Asigna CodigoExterno al campo id para mantener consistencia
                item["id"] = codigo
                
                db.licitaciones.update_one(
                    {"CodigoExterno": codigo},
                    {"$set": item},
                    upsert=True
                )
                procesados += 1

        return {
            "status": "ok",
            "mensaje": "Sincronización exitosa.",
            "total_encontrados": len(listado),
            "guardados_en_db": procesados
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Error de conexión con la API de Mercado Público: {str(e)}"
        )