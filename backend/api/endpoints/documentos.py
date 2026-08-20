from fastapi import APIRouter, HTTPException
from services.ai_service import analizar_anexos_con_ia
from services.doc_generator import generar_propuesta_word, generar_excel_economico

router = APIRouter(prefix="/api/documentos", tags=["Documentos & IA"])

DATOS_COIMSA_DEFAULT = {
    "razon_social": "COIMSA SERVICIOS INTEGRALES SPAL",
    "rut": "76.123.456-7",
    "representante": "José Jiménez"
}

@router.post("/analizar/{id_licitacion}")
def analizar_licitacion(id_licitacion: str):
    resultado = analizar_anexos_con_ia(id_licitacion)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

@router.post("/generar/{id_licitacion}")
def generar_documentos_licitacion(id_licitacion: str, datos_ia: dict):
    try:
        doc_word = generar_propuesta_word(
            id_licitacion=id_licitacion,
            datos_empresa=DATOS_COIMSA_DEFAULT,
            datos_ia=datos_ia,
            nombre_salida="Anexo_Declaracion_Aceptacion"
        )
        doc_excel = generar_excel_economico(
            id_licitacion=id_licitacion,
            datos_ia=datos_ia,
            nombre_salida="Anexo_Propuesta_Economica"
        )
        return {
            "status": "ok",
            "archivos_generados": [doc_word.name, doc_excel.name]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar documentos: {e}")