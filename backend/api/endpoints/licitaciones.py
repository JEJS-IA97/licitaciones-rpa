import requests
import datetime
import re
from fastapi import APIRouter, HTTPException, Query
from config.database import get_db
from config.settings import CHILECOMPRA_TICKET, LICITACIONES_DATA_DIR
from services.ai_service import analizar_anexos_con_ia
from services.doc_generator import generar_propuesta_word, generar_excel_economico
from services.playwright_rpa import descargar_anexos_mp

router = APIRouter(prefix="/api/licitaciones", tags=["Licitaciones"])

# ------------------------------------------------------------
#  FUNCIÓN AUXILIAR: Obtener detalle de la API de Mercado Público
# ------------------------------------------------------------
def _obtener_detalle_api(codigo: str):
    """
    Consulta el detalle completo de una licitación usando la API v1.
    Retorna el objeto 'Licitacion' del listado o None si no existe.
    """
    if not CHILECOMPRA_TICKET:
        return None
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?codigo={codigo}&ticket={CHILECOMPRA_TICKET}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        return listado[0] if listado else None
    except Exception as e:
        print(f"⚠️ Error al obtener detalle de {codigo}: {e}")
        return None

# ------------------------------------------------------------
#  FUNCIÓN: Transformar documento MongoDB/API a formato frontend
# ------------------------------------------------------------
def _formatear_licitacion(doc):
    """
    Convierte el documento (de MongoDB o de la API) al objeto que espera el frontend.
    """
    codigo = doc.get("id") or doc.get("CodigoExterno") or ""
    nombre = doc.get("Nombre") or doc.get("nombre") or ""
    
    estado_codigo = doc.get("CodigoEstado")
    estado_glosa = doc.get("Estado") or ""
    if estado_codigo == 5:
        estado_glosa = "Publicada"
    elif estado_codigo == 7:
        estado_glosa = "Cerrada"
    elif estado_codigo == 6:
        estado_glosa = "Adjudicada"

    fechas_obj = doc.get("Fechas", {})
    fechas = {
        "fecha_publicacion": fechas_obj.get("FechaPublicacion") or doc.get("FechaPublicacion") or "",
        "fecha_cierre": fechas_obj.get("FechaCierre") or doc.get("FechaCierre") or "",
        "fecha_creacion": fechas_obj.get("FechaCreacion") or ""
    }

    comprador = doc.get("Comprador", {})
    institucion = {
        "organismo_comprador": comprador.get("NombreOrganismo") or doc.get("Organismo") or "",
        "rut": comprador.get("RutUnidad") or "",
        "unidad_compra": comprador.get("NombreUnidad") or "",
        "region": comprador.get("RegionUnidad") or "",
        "comuna": comprador.get("ComunaUnidad") or ""
    }

    presupuesto = {
        "monto_disponible": doc.get("MontoEstimado") or 0,
        "moneda": doc.get("Moneda") or "CLP"
    }

    items = doc.get("Items", {})
    productos = []
    if items and items.get("Listado"):
        for item in items["Listado"]:
            productos.append({
                "codigo_producto": item.get("CodigoProducto"),
                "nombre": item.get("NombreProducto") or "",
                "descripcion": item.get("Descripcion") or "",
                "cantidad": item.get("Cantidad"),
                "unidad_medida": item.get("UnidadMedida") or ""
            })

    return {
        "codigo": codigo,
        "nombre": nombre,
        "estado": {"codigo": estado_codigo, "glosa": estado_glosa},
        "fechas": fechas,
        "descripcion": doc.get("Descripcion") or "",
        "institucion": institucion,
        "presupuesto": presupuesto,
        "productos_solicitados": productos,
        "documentos": doc.get("Documentos", []),
        "tipo": doc.get("Tipo") or "",
        "moneda": doc.get("Moneda") or "CLP"
    }

# ------------------------------------------------------------
#  RUTAS (orden correcto: específicas antes que genéricas)
# ------------------------------------------------------------

@router.get("/buscar")
def buscar_licitaciones_api(
    q: str = Query(..., min_length=1),
    tamano_pagina: int = Query(25, ge=1, le=50)
):
    """
    Busca licitaciones en la API de Mercado Público en tiempo real.
    Si q parece un código (ej: 2582-54-LP26), consulta por código.
    Si no, obtiene el listado del día y filtra por nombre/descripción.
    """
    if not CHILECOMPRA_TICKET:
        raise HTTPException(status_code=400, detail="Falta CHILECOMPRA_TICKET")

    # Intentar interpretar como código
    if re.match(r'^\d+-\d+-\w+$', q):
        url = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?codigo={q}&ticket={CHILECOMPRA_TICKET}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            listado = data.get("Listado", [])
            items = [_formatear_licitacion(item) for item in listado]
            return {"payload": {"items": items, "total": len(items)}}
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error al consultar API: {str(e)}")

    # Búsqueda por palabra clave: obtener licitaciones del día y filtrar
    fecha = datetime.datetime.now().strftime("%d%m%Y")
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha={fecha}&ticket={CHILECOMPRA_TICKET}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        listado = data.get("Listado", [])
        # Filtrar por nombre o descripción
        pattern = re.compile(q, re.IGNORECASE)
        filtrados = []
        for item in listado:
            nombre = item.get("Nombre", "")
            desc = item.get("Descripcion", "")
            if pattern.search(nombre) or pattern.search(desc):
                # Obtener detalle completo (opcional, puede ralentizar)
                detalle = _obtener_detalle_api(item.get("CodigoExterno"))
                if detalle:
                    item.update(detalle)
                filtrados.append(item)
        items = [_formatear_licitacion(item) for item in filtrados[:tamano_pagina]]
        return {"payload": {"items": items, "total": len(filtrados)}}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar API: {str(e)}")

@router.get("/guardadas")
def listar_licitaciones_guardadas():
    """
    Retorna todas las licitaciones que el usuario ha guardado en MongoDB.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")
    docs = list(db.licitaciones.find({}, {"_id": 0}))
    items = [_formatear_licitacion(doc) for doc in docs]
    return {"payload": {"items": items, "total": len(items)}}

@router.get("/potenciales")
def listar_potenciales():
    """
    Retorna licitaciones que la IA ha clasificado como relevantes pero no guardadas.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")
    docs = list(db.licitaciones.find(
        {"clasificacion_ia": {"$exists": True}, "guardada_el": {"$exists": False}},
        {"_id": 0}
    ))
    items = [_formatear_licitacion(doc) for doc in docs]
    return {"payload": {"items": items, "total": len(items)}}

@router.post("/guardar/{id_licitacion}")
def guardar_licitacion(id_licitacion: str):
    """
    Guarda una licitación en MongoDB (si no existe).
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")
    if db.licitaciones.find_one({"id": id_licitacion}):
        return {"status": "ok", "mensaje": f"Licitación {id_licitacion} ya está guardada."}
    doc = _obtener_detalle_api(id_licitacion)
    if not doc:
        raise HTTPException(status_code=404, detail="Licitación no encontrada en Mercado Público")
    doc["id"] = id_licitacion
    doc["guardada_el"] = datetime.datetime.utcnow()
    db.licitaciones.insert_one(doc)
    return {"status": "ok", "mensaje": f"Licitación {id_licitacion} guardada correctamente."}

# --- Rutas existentes (deben ir después de las específicas) ---
@router.get("/")
def listar_licitaciones(q: str = None, tamano_pagina: int = 25):
    db = get_db()
    filtro = {}
    if q:
        filtro = {
            "$or": [
                {"Nombre": {"$regex": q, "$options": "i"}},
                {"CodigoExterno": {"$regex": q, "$options": "i"}},
                {"id": {"$regex": q, "$options": "i"}}
            ]
        }
    cursor = db.licitaciones.find(filtro, {"_id": 0}).sort("FechaPublicacion", -1)
    if tamano_pagina:
        cursor = cursor.limit(tamano_pagina)
    docs = list(cursor)
    items = [_formatear_licitacion(doc) for doc in docs]
    return {"payload": {"items": items, "total": len(items)}}

@router.get("/{id_licitacion}")
def obtener_licitacion(id_licitacion: str):
    db = get_db()
    doc = db.licitaciones.find_one({"id": id_licitacion}, {"_id": 0})
    if not doc:
        doc = db.licitaciones.find_one({"CodigoExterno": id_licitacion}, {"_id": 0})
    if not doc or not doc.get("Descripcion"):
        api_doc = _obtener_detalle_api(id_licitacion)
        if api_doc:
            api_doc["id"] = id_licitacion
            db.licitaciones.update_one(
                {"id": id_licitacion},
                {"$set": api_doc},
                upsert=True
            )
            doc = api_doc
        else:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
    return {"payload": _formatear_licitacion(doc)}

@router.post("/{id_licitacion}/analizar")
async def analizar_licitacion(id_licitacion: str):
    anexos_dir = LICITACIONES_DATA_DIR / id_licitacion / "anexos_originales"
    if not anexos_dir.exists() or not any(anexos_dir.iterdir()):
        resultado = await descargar_anexos_mp(id_licitacion)
        if resultado.get("status") == "error":
            raise HTTPException(status_code=500, detail=resultado.get("detalle"))
        if resultado.get("status") == "warning":
            raise HTTPException(status_code=400, detail="No se encontraron anexos para descargar")
    resultado_ia = analizar_anexos_con_ia(id_licitacion)
    if "error" in resultado_ia:
        raise HTTPException(status_code=400, detail=resultado_ia["error"])
    return {"payload": resultado_ia}

@router.post("/{id_licitacion}/aplicar")
def aplicar_licitacion(id_licitacion: str, payload: dict):
    datos_ia = payload.get("datos_ia", {})
    if not datos_ia:
        raise HTTPException(status_code=400, detail="Faltan datos de IA en el payload")
    DATOS_COIMSA_DEFAULT = {
        "razon_social": "COIMSA SERVICIOS INTEGRALES SPAL",
        "rut": "76.123.456-7",
        "representante": "José Jiménez"
    }
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

@router.post("/sincronizar")
def sincronizar_licitaciones_activas():
    if not CHILECOMPRA_TICKET:
        raise HTTPException(status_code=400, detail="Falta CHILECOMPRA_TICKET")
    db = get_db()
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
            return {"status": "ok", "mensaje": "No se encontraron licitaciones activas.", "guardados": 0}
        procesados = 0
        for item in listado:
            codigo = item.get("CodigoExterno")
            if codigo:
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
            "guardados": procesados
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error de conexión: {str(e)}")

@router.post("/scrapear")
def scrapear_licitaciones():
    try:
        from modules.scraper import procesar_y_guardar_licitaciones
        nuevas = procesar_y_guardar_licitaciones()
        return {
            "status": "ok",
            "nuevas_encontradas": len(nuevas),
            "licitaciones": nuevas
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="Módulo scraper no encontrado")