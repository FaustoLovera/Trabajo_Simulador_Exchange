import json
import os
from decimal import Decimal
from config import COTIZACIONES_PATH

# Caché en memoria para almacenar los precios de las criptomonedas.
# Esto evita leer el archivo JSON en cada consulta, mejorando el rendimiento.
precios_cache = {}

def cargar_datos_cotizaciones():
    """
    Carga la lista de cotizaciones desde el archivo JSON de forma segura.

    Esta función lee el archivo definido en `COTIZACIONES_PATH`. Si el archivo
    no existe, está vacío o su contenido JSON es inválido, devuelve una lista vacía
    para evitar errores en el resto de la aplicación.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada diccionario representa
                    una criptomoneda con sus datos (ej. ticker, precio_usd).
                    Retorna una lista vacía si la carga falla.

    Example:
        >>> # Suponiendo que cotizaciones.json contiene: 
        >>> # [{'ticker': 'BTC', 'precio_usd': '65000.00'}]
        >>> datos = cargar_datos_cotizaciones()
        >>> print(datos)
        [{'ticker': 'BTC', 'precio_usd': '65000.00'}]
    """
    if not os.path.exists(COTIZACIONES_PATH) or os.path.getsize(COTIZACIONES_PATH) == 0:
        return []

    try:
        with open(COTIZACIONES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Si hay un error de decodificación o el archivo no se encuentra, 
        # se retorna una lista vacía para manejar el error de forma controlada.
        return []

def recargar_cache_precios():
    """
    Actualiza el caché de precios en memoria (`precios_cache`) a partir del archivo JSON.

    Esta función debe ser llamada cada vez que los datos de cotizaciones en el
    archivo `cotizaciones.json` son actualizados. Lee los datos y los carga en el
    diccionario `precios_cache` para un acceso rápido y eficiente.

    Side Effects:
        Modifica la variable global `precios_cache`.
    """
    global precios_cache
    print("🔄 Recargando caché de precios...")
    lista_criptos = cargar_datos_cotizaciones()
    
    # Crea un diccionario con el ticker en mayúsculas como clave y el precio como Decimal.
    precios_cache = {
        cripto.get("ticker", "").upper(): Decimal(str(cripto.get("precio_usd", "0")))
        for cripto in lista_criptos
    }
    print("✅ Caché de precios actualizado.")


def obtener_precio(ticker):
    """
    Obtiene el precio de una criptomoneda específica desde el caché en memoria.

    Si el caché de precios está vacío, llama a `recargar_cache_precios()` para cargarlo.
    La búsqueda del ticker no distingue entre mayúsculas y minúsculas.

    Args:
        ticker (str): El ticker de la criptomoneda a consultar (ej. "BTC", "eth").

    Returns:
        Decimal | None: El precio de la criptomoneda como un objeto Decimal si se encuentra.
                        Retorna `None` si el ticker no existe en el caché.

    Example:
        >>> # Suponiendo que el caché ha sido cargado con {'BTC': Decimal('65000.00')}
        >>> precio_btc = obtener_precio("btc")
        >>> print(precio_btc)
        Decimal('65000.00')
        
        >>> precio_luna = obtener_precio("LUNA")
        >>> print(precio_luna)
        None
    """
    # Si el caché está vacío, se carga por primera vez.
    if not precios_cache:
        recargar_cache_precios()
    
    # Devuelve el precio del ticker (en mayúsculas) o None si no se encuentra.
    return precios_cache.get(ticker.upper())