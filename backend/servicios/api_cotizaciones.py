"""
Servicio para interactuar con APIs externas de criptomonedas.

Este módulo centraliza las llamadas a las APIs de CoinGecko (para cotizaciones
generales del mercado) y Binance (para datos de velas/k-lines). Se encarga de
realizar las peticiones, procesar los datos y guardarlos localmente.
"""

from decimal import Decimal
import requests
import json
# === INICIO DE LA MODIFICACIÓN ===
# La importación ahora apunta a la capa de acceso a datos, que es más correcto.
from backend.acceso_datos.datos_cotizaciones import guardar_datos_cotizaciones
# === FIN DE LA MODIFICACIÓN ===
from config import COINGECKO_URL, BINANCE_URL, CANTIDAD_CRIPTOMONEDAS, CANTIDAD_VELAS

def obtener_datos_criptos_coingecko() -> list[dict]:
    """
    Obtiene y procesa datos de mercado desde la API de CoinGecko.

    Realiza una petición para obtener una lista de las principales criptomonedas,
    procesa la respuesta JSON y guarda los datos crudos en un archivo local.
    El formateo para la UI se delega a otra capa de servicio.
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": CANTIDAD_CRIPTOMONEDAS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }

    try:
        respuesta = requests.get(COINGECKO_URL, params, timeout=10)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de CoinGecko: {str(e)}")
        return []

    print(f"✅ Estado de la respuesta CoinGecko: {respuesta.status_code}")

    try:
        datos = respuesta.json()
        resultado = []
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


def obtener_velas_de_api(ticker: str, interval: str) -> list[dict]:
    """
    Obtiene datos históricos de velas (K-lines) desde la API de Binance.
    """
    params = {
        "symbol": f"{ticker.upper()}USDT",
        "interval": interval,
        "limit": CANTIDAD_VELAS,
    }
    try:
        respuesta = requests.get(BINANCE_URL, params, timeout=10)
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
        
        resultado = [
            {
                "time": int(vela[0] / 1000), "open": str(Decimal(vela[1])),
                "high": str(Decimal(vela[2])), "low": str(Decimal(vela[3])),
                "close": str(Decimal(vela[4])), "volume": str(Decimal(vela[5])),
            }
            for vela in datos
        ]
        return resultado
    except (json.JSONDecodeError, IndexError, TypeError) as e:
        print(f"❌ Error al procesar los datos de velas de Binance para {ticker}: {e}")
        return []