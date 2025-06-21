import json
import os
from decimal import Decimal
from config import COTIZACIONES_PATH

precios_cache = {}

def cargar_datos_cotizaciones():
    """
    Función interna y segura para cargar todas las cotizaciones del archivo JSON.
    Maneja archivos inexistentes o corruptos.
    """
    if not os.path.exists(COTIZACIONES_PATH) or os.path.getsize(COTIZACIONES_PATH) == 0:
        return []

    try:
        with open(COTIZACIONES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def recargar_cache_precios():
    """
    Actualiza el diccionario de caché de precios en memoria desde el archivo JSON.
    Debe ser llamada después de que los datos de cotizaciones se actualizan.
    """
    global precios_cache
    print("🔄 Recargando caché de precios...")
    lista_criptos = cargar_datos_cotizaciones()
    
    precios_cache = {
        cripto.get("ticker", "").upper(): Decimal(str(cripto.get("precio_usd", "0")))
        for cripto in lista_criptos
    }
    print("✅ Caché de precios actualizado.")


def obtener_precio(ticker):
    """
    Obtiene el precio de un ticker específico desde el caché en memoria.
    Si el caché está vacío, lo carga por primera vez.
    """
    if not precios_cache:
        recargar_cache_precios()
    
    return precios_cache.get(ticker.upper())