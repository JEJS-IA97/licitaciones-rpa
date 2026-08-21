import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from config.settings import LICITACIONES_DATA_DIR

async def descargar_anexos_mp(id_licitacion: str):
    """
    Navega a la ficha de la licitación en Mercado Público y descarga los anexos.
    """
    dir_descarga = LICITACIONES_DATA_DIR / id_licitacion / "anexos_originales"
    dir_descarga.mkdir(parents=True, exist_ok=True)

    url_ficha = f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={id_licitacion}"
    archivos_descargados = []

    print(f"🤖 Iniciando Playwright para licitación: {id_licitacion}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        try:
            await page.goto(url_ficha, wait_until="domcontentloaded", timeout=60000)
            
            enlaces_descarga = await page.locator("a[href*='Download'], a[title*='Descargar'], a.btn-descargar").all()

            for enlace in enlaces_descarga:
                try:
                    async with page.expect_download(timeout=15000) as download_info:
                        await enlace.click()
                    
                    download = await download_info.value
                    nombre_seguro = download.suggested_filename.replace("/", "-").replace("\\", "-")
                    ruta_final = dir_descarga / nombre_seguro
                    
                    await download.save_as(str(ruta_final))
                    archivos_descargados.append(nombre_seguro)
                    print(f"✅ Descargado: {nombre_seguro}")
                    
                except Exception as e_dl:
                    print(f"⚠️ Omitida descarga individual: {e_dl}")
                    continue

        except Exception as e:
            print(f"❌ Error en navegación Playwright: {e}")
            return {"status": "error", "detalle": str(e)}
        finally:
            await browser.close()

    if archivos_descargados:
        return {"status": "ok", "archivos": archivos_descargados, "ruta": str(dir_descarga)}
    
    return {"status": "warning", "mensaje": "Navegación finalizada sin descargas detectadas."}