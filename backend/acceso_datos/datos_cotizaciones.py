"""
Módulo de acceso a datos de cotizaciones.

Este módulo utiliza un patrón de fábrica (closure) para gestionar un caché de precios
en memoria de forma segura, evitando el uso de variables globales explícitas.

Expone públicamente:
- obtener_precio(ticker): Obtiene el precio de una cripto, usando el caché.
- cargar_datos_cotizaciones(): Carga la lista de cotizaciones desde el archivo.
- guardar_datos_cotizaciones(data): Guarda las cotizaciones en el archivo y
  automáticamente actualiza el caché.
"""

import json
import os
from decimal import Decimal
from typing import Callable, Tuple, Any

from config import COTIZACIONES_PATH


# Función fábrica
def _crear_gestor_cache_precios() -> Tuple[Callable[[str], Decimal | None], Callable[[], None]]:
    """
    Función de fábrica interna que crea un gestor de caché de precios.

    Usa un closure para encapsular el diccionario del caché (_cache), protegiéndolo
    del acceso externo y eliminando la necesidad de variables globales o de módulo.

    Returns:
        Una tupla con dos funciones que operan sobre el mismo caché encapsulado:
        - La función para obtener un precio.
        - La función para forzar una recarga del caché.
    """
    _cache = {}  # Este diccionario es privado y solo vive en este módulo.

    def _recargar_desde_archivo():
        """
        Función interna y privada que lee el archivo JSON y puebla el caché.
        Modifica la variable `_cache` de su closure.
        """
        nonlocal _cache
        print("🔄 Recargando caché de precios desde el archivo...")
        
        if not os.path.exists(COTIZACIONES_PATH) or os.path.getsize(COTIZACIONES_PATH) == 0:
            lista_criptos = []
        else:
            try:
                with open(COTIZACIONES_PATH, "r", encoding="utf-8") as f:
                    lista_criptos = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                lista_criptos = []
        
        _cache = {
            cripto.get("ticker", "").upper(): Decimal(str(cripto.get("precio_usd", "0")))
            for cripto in lista_criptos
        }
        print("✅ Caché de precios actualizado en memoria.")

    def obtener_precio_desde_cache(ticker: str) -> Decimal | None:
        """
        Obtiene el precio de un ticker desde el caché.
        Si el caché está vacío, dispara la recarga la primera vez.
        """
        if not _cache:
            _recargar_desde_archivo()
        
        return _cache.get(ticker.upper())

    def forzar_recarga_cache():
        """Función pública para forzar la recarga del caché."""
        _recargar_desde_archivo()

    # La fábrica devuelve las dos funciones que el resto de la app usará.
    return obtener_precio_desde_cache, forzar_recarga_cache

# --- Punto de Entrada del Módulo ---

# 1. Llamamos a la fábrica UNA SOLA VEZ cuando se importa este módulo.
# 2. Se crea un caché privado y dos funciones ('_obtener', '_recargar') que lo gestionan.
# 3. Asignamos esas funciones a nombres a nivel de módulo que serán exportados.
_obtener, _recargar = _crear_gestor_cache_precios()


# --- API Pública del Módulo ---

def obtener_precio(ticker: str) -> Decimal | None:
    """
    Interfaz pública para obtener el precio de una criptomoneda desde el caché.
    """
    return _obtener(ticker)


def cargar_datos_cotizaciones() -> list[dict]:
    """
    Interfaz pública para cargar la lista completa de cotizaciones desde el archivo.
    Esto es necesario para el módulo de presentación que formatea todos los datos.
    """
    if not os.path.exists(COTIZACIONES_PATH) or os.path.getsize(COTIZACIONES_PATH) == 0:
        return []
    try:
        with open(COTIZACIONES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def guardar_datos_cotizaciones(data: list[dict[str, Any]]):
    """
    Interfaz pública para guardar los datos de cotizaciones en el archivo.
    Después de guardar, fuerza automáticamente la recarga del caché en memoria.
    """
    os.makedirs(os.path.dirname(COTIZACIONES_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_cotizaciones.json...")
    try:
        with open(COTIZACIONES_PATH, "w") as archivo:
            # Usar un default handler para convertir Decimal a float en la serialización.
            # Esto es solo si los datos de entrada contienen Decimals, lo cual no debería ser el caso.
            json.dump(data, archivo, indent=4)
        print("✅ Datos de cotizaciones guardados en archivo.")
        # Llama a la función de recarga para mantener el caché sincronizado.
        _recargar()
    except (IOError, TypeError) as e:
        print(f"❌ Error al guardar el archivo de cotizaciones: {e}")