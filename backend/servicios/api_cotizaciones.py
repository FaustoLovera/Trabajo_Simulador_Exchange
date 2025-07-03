"""Adaptador de APIs Externas para la Ingesta de Datos de Mercado.

Este módulo actúa como una capa de abstracción (Facade/Adapter) que aísla al
resto de la aplicación de las complejidades de las APIs de terceros (CoinGecko,
Binance). Su responsabilidad sigue un patrón ETL (Extract, Transform, Load):

-   **Extract**: Realiza peticiones HTTP a los endpoints de las APIs externas.
-   **Transform**: Procesa las respuestas JSON, las limpia, y las mapea a un
    esquema de datos interno y estandarizado para el simulador.
-   **Load**: Persiste los datos transformados en un archivo local (JSON) que
    funciona como una caché para minimizar las llamadas a la API y mejorar
    el rendimiento.
"""

from decimal import Decimal
import requests
import json
from typing import Any, Dict, List

from backend.acceso_datos.datos_cotizaciones import guardar_datos_cotizaciones
import config

def obtener_datos_criptos_coingecko() -> List[Dict[str, Any]]:
    """Implementa el pipeline ETL para los datos de mercado de CoinGecko.

    1.  **Extract**: Realiza una petición GET a la API de CoinGecko para obtener
        las principales criptomonedas por capitalización de mercado.
    2.  **Transform**: Itera sobre la respuesta JSON. Cada objeto de criptomoneda
        es mapeado a un diccionario con una estructura interna definida.
        Los valores numéricos se convierten a `Decimal` para precisión y luego
        a `str` para su almacenamiento serializado en JSON.
    3.  **Load**: Llama a `guardar_datos_cotizaciones` para persistir la lista
        transformada en un archivo local, que actúa como caché.

    Returns:
        Una lista de diccionarios con el formato interno estandarizado.
        Retorna una lista vacía si ocurre cualquier error de red o de parseo.

    Side Effects:
        - Sobrescribe el archivo de cotizaciones (`cotizaciones.json`) con los
          nuevos datos obtenidos.
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": config.CANTIDAD_CRIPTOMONEDAS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }

    try:
        respuesta = requests.get(config.COINGECKO_URL, params, timeout=10)
        respuesta.raise_for_status()
    except Exception as e:
        print(f"❌ Error al obtener datos de CoinGecko: {str(e)}")
        return []

    print(f"✅ Estado de la respuesta CoinGecko: {respuesta.status_code}")

    try:
        datos = respuesta.json()
        resultado = []
        
        # Itera sobre los datos recibidos de la API de cada criptomoneda, comenzando en 1.
        for i, dato in enumerate(datos, start=1):
            resultado.append({
                "id": i,
                "nombre": dato.get("name"),
                "ticker": dato.get('symbol', '').upper(),
                "logo": dato.get("image"),
                "precio_usd": str(Decimal(str(dato.get("current_price", 0)))),
                "1h_%": str(Decimal(str(dato.get("price_change_percentage_1h_in_currency", 0)))),
                "24h_%": str(Decimal(str(dato.get("price_change_percentage_24h_in_currency", 0)))),
                "7d_%": str(Decimal(str(dato.get("price_change_percentage_7d_in_currency", 0)))),
                "market_cap": str(Decimal(str(dato.get("market_cap", 0)))),
                "volumen_24h": str(Decimal(str(dato.get("total_volume", 0)))),
                "circulating_supply": str(Decimal(str(dato.get("circulating_supply", 0)))),
            })
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        print(f"❌ Error al procesar los datos de CoinGecko: {str(e)}")
        return []

    print(f"💡 Total de criptos procesadas: {len(resultado)}")
    guardar_datos_cotizaciones(resultado)
    return resultado


def obtener_velas_de_api(ticker: str, interval: str) -> List[Dict[str, Any]]:
    """Obtiene y transforma datos de velas (K-lines) desde la API de Binance.

    Realiza una petición a la API de Binance y transforma la respuesta, que es
    una lista de listas, en un formato más legible y útil para el frontend:
    una lista de diccionarios con claves explícitas (timestamp, open, high, etc.).

    Args:
        ticker: El ticker del par a consultar (ej. "BTC"). Se le añade "USDT"
                automáticamente para formar el par de trading.
        interval: El intervalo de tiempo para las velas (ej. "1h", "4h", "1d").

    Returns:
        Una lista de diccionarios, donde cada uno representa una vela. Devuelve
        una lista vacía si ocurre un error de red o de formato de datos.
    """
    params = {
        "symbol": f"{ticker.upper()}USDT",
        "interval": interval,
        "limit": config.CANTIDAD_VELAS,
    }
    try:
        respuesta = requests.get(config.BINANCE_URL, params, timeout=10)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de Binance para {ticker} ({interval}): {str(e)}")
        return []

    print(f"✅ Estado de la respuesta Binance para {ticker} ({interval}): {respuesta.status_code}")

    try:
        datos = respuesta.json()
        if not isinstance(datos, list):
            print(f"⚠️ Respuesta inesperada de Binance para {ticker} ({interval}): {datos}")
            return []
        
        # La API de Binance devuelve una lista de listas.
        # Cada sub-lista se mapea a un diccionario con claves descriptivas.
        # El timestamp se convierte de milisegundos a segundos.
        resultado = [
            {
                "time": int(vela[0] / 1000),
                "open": str(Decimal(vela[1])),
                "high": str(Decimal(vela[2])),
                "low": str(Decimal(vela[3])),
                "close": str(Decimal(vela[4])),
                "volume": str(Decimal(vela[5])),
            }
            for vela in datos
        ]
        return resultado
    except (json.JSONDecodeError, IndexError, TypeError) as e:
        print(f"❌ Error al procesar los datos de velas de Binance para {ticker}: {e}")
        return []