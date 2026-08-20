import json
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from openai import OpenAI
from google import genai
from anthropic import Anthropic

from config.settings import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    DEEPSEEK_API_KEY,
    CLAUDE_API_KEY,
    LICITACIONES_DATA_DIR
)

# Inicialización segura de clientes
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
) if DEEPSEEK_API_KEY else None


def extraer_texto_archivo(path_archivo: Path) -> str:
    extension = path_archivo.suffix.lower()
    texto = ""
    try:
        if extension == ".pdf":
            reader = PdfReader(str(path_archivo))
            for page in reader.pages:
                texto += page.extract_text() or ""
        elif extension == ".docx":
            doc = Document(str(path_archivo))
            for p in doc.paragraphs:
                texto += p.text + "\n"
    except Exception as e:
        print(f"⚠️ Error al leer {path_archivo.name}: {e}")
    return texto


def analizar_anexos_con_ia(id_licitacion: str) -> dict:
    dir_anexos = LICITACIONES_DATA_DIR / id_licitacion / "anexos_originales"
    if not dir_anexos.exists():
        return {"error": "No se encontraron anexos descargados para esta licitación."}

    archivos = list(dir_anexos.glob("*.*"))
    if not archivos:
        return {"error": "La carpeta de anexos está vacía."}

    contenido_consolidado = ""
    for archivo in archivos:
        contenido_consolidado += f"\n--- INICIO ARCHIVO: {archivo.name} ---\n"
        contenido_consolidado += extraer_texto_archivo(archivo)
        contenido_consolidado += f"\n--- FIN ARCHIVO: {archivo.name} ---\n"

    texto_recortado = contenido_consolidado[:14000]

    prompt_base = """
    Analiza los siguientes pliegos/anexos de Mercado Público y extrae la información en un JSON estricto:
    {
      "cargo_licitacion": "Nombre del servicio o mantención",
      "requiere_personal": true/false,
      "personal_solicitado": [
        {"cargo": "Ejemplo Cargo", "cantidad": 1, "remuneracion_minima": 0}
      ],
      "insumos_y_maquinaria": ["Lista de insumos requeridos"],
      "anexos_obligatorios": [
        {"nombre_anexo": "Nombre Anexo", "formato_requerido": "PDF/Excel/Word"}
      ],
      "garantias_solicitadas": "Detalles de garantías",
      "observaciones_clave": "Fechas límites, restricciones o notas importantes"
    }
    """

    res_openai_json = {}
    res_deepseek_txt = ""
    res_claude_txt = ""

    # --- PASO 1: OpenAI (Si falla o agota saldo, salta) ---
    if openai_client:
        try:
            res_openai = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_base},
                    {"role": "user", "content": texto_recortado}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            res_openai_json = json.loads(res_openai.choices[0].message.content)
            print("✅ Paso 1: OpenAI procesado con éxito.")
        except Exception as e:
            print(f"⚠️ OpenAI omitido (Límite de cuota o error): {e}")

    # --- PASO 2: DeepSeek (Si falla o agota saldo, salta) ---
    if deepseek_client:
        try:
            res_ds = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Eres un auditor financiero para licitaciones públicas."},
                    {"role": "user", "content": f"Revisa este borrador:\n{json.dumps(res_openai_json, ensure_ascii=False)}\n\nTexto original:\n{texto_recortado}"}
                ],
                temperature=0.1
            )
            res_deepseek_txt = res_ds.choices[0].message.content
            print("✅ Paso 2: DeepSeek procesado con éxito.")
        except Exception as e:
            print(f"⚠️ DeepSeek omitido (Límite de cuota o error): {e}")

    # --- PASO 3: Claude / Anthropic (Si falla o agota saldo, salta) ---
    if anthropic_client:
        try:
            res_claude = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.1,
                system="Eres un experto legal en pliegos de Mercado Público Chile.",
                messages=[
                    {"role": "user", "content": f"Verifica si faltan anexos requeridos:\n{texto_recortado}"}
                ]
            )
            res_claude_txt = res_claude.content[0].text
            print("✅ Paso 3: Claude procesado con éxito.")
        except Exception as e:
            print(f"⚠️ Claude omitido (Límite de cuota o error): {e}")

    # --- PASO 4: Consolidación Final con Gemini (Respaldo Gratuito Principal) ---
    if gemini_client:
        try:
            prompt_sintesis = f"""
            Actúas como Director General de Licitaciones.
            Consolida los hallazgos de las herramientas disponibles y devuelve el JSON estricto final.

            [DATOS PARCIALES / PRELIMINARES]:
            OpenAI: {json.dumps(res_openai_json, ensure_ascii=False)}
            DeepSeek: {res_deepseek_txt}
            Claude: {res_claude_txt}

            [TEXTO COMPLETO DE ANEXOS]:
            {texto_recortado}

            Devuelve ÚNICAMENTE la estructura JSON requerida con la mejor información consolidada.
            """

            res_gemini = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_sintesis,
                config={'response_mime_type': 'application/json'}
            )
            print("✅ Consolidación final con Gemini completada.")
            return json.loads(res_gemini.text)
        except Exception as e:
            print(f"❌ Error en Gemini: {e}")

    # Si Gemini falla pero OpenAI respondió, devuelve la respuesta de OpenAI
    if res_openai_json:
        return res_openai_json

    return {"error": "Todas las APIs superaron su límite gratuito o fallaron."}