# services/playwright_rpa.py

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from config.settings import LICITACIONES_DATA_DIR

async def descargar_anexos_mp(id_licitacion: str, url_anexos: str = None):
    """
    Descarga todos los anexos de una licitación desde la página de anexos.
    """
    if not url_anexos:
        return {"status": "error", "detalle": "Se requiere la URL de anexos"}
    
    carpeta_destino = LICITACIONES_DATA_DIR / id_licitacion / "anexos_originales"
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        try:
            print(f"📄 Navegando a la página de anexos de {id_licitacion}...")
            await page.goto(url_anexos, wait_until="domcontentloaded", timeout=60000)
            
            # Esperar a que cargue la tabla
            await page.wait_for_selector('input[title="Ver Anexo"]', timeout=30000)
            
            botones = await page.locator('input[title="Ver Anexo"]').all()
            archivos_descargados = []
            
            for i, boton in enumerate(botones):
                try:
                    async with page.expect_download(timeout=30000) as download_info:
                        await boton.click()
                    download = await download_info.value
                    nombre_archivo = download.suggested_filename or f"anexo_{i+1}.pdf"
                    nombre_archivo = nombre_archivo.replace('/', '-').replace('\\', '-')
                    ruta_final = carpeta_destino / nombre_archivo
                    await download.save_as(str(ruta_final))
                    archivos_descargados.append(nombre_archivo)
                    print(f"✅ Descargado: {nombre_archivo}")
                except Exception as e:
                    print(f"⚠️ Error en anexo {i+1}: {e}")
                    continue
            
            await browser.close()
            return {
                "status": "ok",
                "archivos": archivos_descargados,
                "ruta": str(carpeta_destino),
                "total": len(archivos_descargados)
            }
            
        except Exception as e:
            await browser.close()
            return {"status": "error", "detalle": str(e)}