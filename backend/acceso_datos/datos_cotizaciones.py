"""Módulo de acceso a datos de cotizaciones de criptomonedas.

Este módulo gestiona la carga y guardado de datos de cotizaciones desde un
archivo JSON. Para optimizar el acceso a los precios, utiliza un caché en
memoria que se carga bajo demanda la primera vez que se solicita un precio.
"""

import json
import os
from decimal import Decimal
from typing import Any, Optional

import config

# Caché de precios en memoria para un acceso rápido y eficiente.
# Se puebla bajo demanda y las claves (tickers) se guardan en mayúsculas.
# Formato: {'TICKER': {'ticker': 'TICKER', 'precio_usd': '123.45', ...}}
_cache_precios: dict[str, dict[str, Any]] = {}

def limpiar_cache_precios():
    """Limpia el caché de precios en memoria.

    Esta función es esencial para el aislamiento de las pruebas, permitiendo
    que cada test se ejecute en un estado limpio sin ser afectado por los
    datos de pruebas anteriores.

    Side Effects:
        - Modifica la variable global `_cache_precios`, reiniciándola a un
          diccionario vacío.
    """
    global _cache_precios
    _cache_precios = {}
    print("🧹 Caché de precios limpiado.")

def recargar_cache_precios(ruta_archivo: Optional[str] = None):
    """Recarga el caché de precios desde un archivo JSON.

    Esta función lee el archivo de cotizaciones, lo procesa y actualiza la
    variable global `_cache_precios`. Está diseñada para ser llamada
    internamente o para fines de prueba.

    Args:
        ruta_archivo (Optional[str]): La ruta al archivo JSON de cotizaciones.
                                     Si es None, usa la ruta de config.

    Side Effects:
        - Modifica la variable global `_cache_precios`.
    """
    ruta_a_usar = ruta_archivo or config.COTIZACIONES_PATH
    global _cache_precios
    print(f"🔄 Recargando caché de precios desde '{ruta_a_usar}'...")

    if not os.path.exists(ruta_a_usar) or os.path.getsize(ruta_a_usar) == 0:
        lista_criptos = []
    else:
        try:
            with open(ruta_a_usar, "r", encoding="utf-8") as f:
                lista_criptos = json.load(f)
        except Exception as e:
            print(f"⚠️ No se pudo leer el archivo de cotizaciones en '{ruta_a_usar}'. Se usará una lista vacía. Error: {e}")
            lista_criptos = []

    _cache_precios = {}
    
    for cripto in lista_criptos:
        ticker = cripto.get("ticker")
        
        if isinstance(ticker, str) and ticker:
            _cache_precios[ticker.upper()] = cripto
    
    print("✅ Caché de precios actualizado en memoria.")

def obtener_precio(ticker: str, ruta_archivo: Optional[str] = None) -> Optional[Decimal]:
    """Obtiene el precio de un activo, con opción de recarga forzada desde una ruta.

    Si se proporciona una `ruta_archivo`, fuerza la recarga del caché desde esa
    ruta. Si no, utiliza el caché existente o lo carga perezosamente si está vacío.
    Esto es crucial para que los tests puedan operar con datos aislados.

    Args:
        ticker (str): El ticker del activo (ej. 'BTC'), insensible a mayúsculas.
        ruta_archivo (Optional[str], optional): Ruta al archivo JSON para forzar
            la recarga. Por defecto None.

    Returns:
        Optional[Decimal]: El precio como un objeto Decimal si se encuentra,
                           o None si el ticker no existe.
    """
    # Si se pasa una ruta, se fuerza la recarga. Si no, se usa lazy-loading.
    if ruta_archivo:
        recargar_cache_precios(ruta_archivo)
    elif not _cache_precios:
        recargar_cache_precios()

    info_cripto = _cache_precios.get(ticker.upper())
    if info_cripto and "precio_usd" in info_cripto:
        return Decimal(str(info_cripto["precio_usd"]))
    
    return None

def cargar_datos_cotizaciones(ruta_archivo: Optional[str] = None) -> list[dict]:
    """Carga y devuelve la lista completa de cotizaciones desde el archivo JSON.

    Esta función lee directamente del disco sin interactuar con el caché. Es ideal
    para obtener la lista completa de activos para mostrar en la interfaz.

    Args:
        ruta_archivo (str): La ruta al archivo JSON de cotizaciones.

    Returns:
        list[dict]: Una lista de diccionarios con los datos de las cotizaciones.
                    Devuelve una lista vacía en caso de error.
    """
    ruta_a_usar = ruta_archivo or config.COTIZACIONES_PATH
    if not os.path.exists(ruta_a_usar) or os.path.getsize(ruta_a_usar) == 0:
        return []
    try:
        with open(ruta_a_usar, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Advertencia: No se pudo leer o el archivo '{ruta_a_usar}' está corrupto. Error: {e}")
        return []

def guardar_datos_cotizaciones(data: list[dict[str, Any]], ruta_archivo: Optional[str] = None):
    """Guarda los datos de cotizaciones y recarga el caché para mantener consistencia.

    Escribe la lista de datos en el archivo JSON. Si el archivo modificado es el
    que usa la aplicación principal, se fuerza una recarga del caché para que
    los cambios se reflejen inmediatamente en el sistema.

    Args:
        data (list[dict[str, Any]]): La lista de cotizaciones a guardar.
        ruta_archivo (str): La ruta del archivo donde se guardarán los datos.

    Side Effects:
        - Escribe o sobrescribe un archivo en disco.
        - Puede disparar una recarga del caché de precios.
    """
    ruta_a_usar = ruta_archivo or config.COTIZACIONES_PATH
    print(f"💾 Guardando datos en '{ruta_a_usar}'...")
    try:
        with open(ruta_a_usar, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("✅ Datos de cotizaciones guardados en archivo.")

        # Forzar recarga del caché desde la ruta usada para mantener consistencia.
        recargar_cache_precios(ruta_a_usar)

    except Exception as e:
        print(f"❌ Error al guardar los datos de cotizaciones: {e}")