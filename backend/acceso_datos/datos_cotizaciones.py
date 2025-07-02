"""
Módulo de acceso a datos de cotizaciones.

Este módulo utiliza un diccionario a nivel de módulo como caché de precios para
mayor simplicidad y claridad. El caché se carga bajo demanda.

Expone públicamente:
- obtener_precio(ticker): Obtiene el precio de una cripto, usando el caché.
- recargar_cache_precios(): Fuerza la recarga del caché desde el archivo.
- cargar_datos_cotizaciones(): Carga la lista de cotizaciones desde el archivo.
- guardar_datos_cotizaciones(data): Guarda las cotizaciones y actualiza el caché.
"""

import json
import os
from decimal import Decimal
from typing import Any

from config import COTIZACIONES_PATH

# El caché es ahora un diccionario explícito a nivel de módulo.
_cache_precios: dict[str, Decimal] = {}

def recargar_cache_precios(ruta_archivo=COTIZACIONES_PATH):
    """
    Lee el archivo JSON y puebla el caché de precios.
    Esta función ahora es pública y puede ser llamada desde los tests para
    inyectar diferentes fuentes de datos.
    """
    global _cache_precios
    print(f"🔄 Recargando caché de precios desde '{ruta_archivo}'...")

    if not os.path.exists(ruta_archivo) or os.path.getsize(ruta_archivo) == 0:
        lista_criptos = []
    else:
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                lista_criptos = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️ No se pudo leer el archivo de cotizaciones en '{ruta_archivo}'. Se usará una lista vacía.")
            lista_criptos = []

    _cache_precios = {
        cripto.get("ticker", "").upper(): Decimal(str(cripto.get("precio_usd", "0")))
        for cripto in lista_criptos
        if cripto.get("ticker")  # Asegurarse de que el ticker no sea None o vacío
    }
    print("✅ Caché de precios actualizado en memoria.")

def obtener_precio(ticker: str) -> Decimal | None:
    """
    Obtiene el precio desde el caché. Si está vacío, lo carga primero.
    """
    if not _cache_precios:
        recargar_cache_precios()
    
    return _cache_precios.get(ticker.upper())

def cargar_datos_cotizaciones(ruta_archivo=COTIZACIONES_PATH) -> list[dict]:
    """
    Carga la lista completa de cotizaciones desde el archivo.
    Esto es necesario para el módulo de presentación que formatea todos los datos.
    """
    if not os.path.exists(ruta_archivo) or os.path.getsize(ruta_archivo) == 0:
        return []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_datos_cotizaciones(data: list[dict[str, Any]], ruta_archivo=COTIZACIONES_PATH):
    """
    Guarda los datos de cotizaciones en el archivo.
    Después de guardar, fuerza automáticamente la recarga del caché en memoria si
    la ruta de guardado es la misma que la de configuración principal.
    """
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
    print(f"💾 Guardando datos en '{ruta_archivo}'...")
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(data, archivo, indent=4)
        print("✅ Datos de cotizaciones guardados en archivo.")
        
        # Si la ruta guardada es la misma que la de configuración, recargamos el caché global.
        if ruta_archivo == COTIZACIONES_PATH:
            recargar_cache_precios()
            
    except (IOError, TypeError) as e:
        print(f"❌ Error al guardar el archivo de cotizaciones: {e}")