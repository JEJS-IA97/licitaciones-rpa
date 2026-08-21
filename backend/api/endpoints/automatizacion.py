from fastapi import APIRouter, HTTPException
from services.playwright_rpa import descargar_anexos_mp

router = APIRouter(prefix="/api/rpa", tags=["Automatización Playwright"])

@router.post("/descargar-anexos/{id_licitacion}")
async def endpoint_descargar_anexos(id_licitacion: str):
    resultado = await descargar_anexos_mp(id_licitacion)
    if resultado.get("status") == "error":
        raise HTTPException(status_code=500, detail=resultado.get("detalle"))
    return resultado