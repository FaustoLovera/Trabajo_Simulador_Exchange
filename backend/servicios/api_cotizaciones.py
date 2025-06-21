"""
Servicio para interactuar con APIs externas de criptomonedas.

Este módulo centraliza las llamadas a las APIs de CoinGecko (para cotizaciones
generales del mercado) y Binance (para datos de velas/k-lines). Se encarga de
realizar las peticiones, procesar los datos y guardarlos localmente.
"""

from decimal import Decimal
import requests
from backend.servicios.velas_logica import guardar_datos_cotizaciones
from config import COINGECKO_URL, BINANCE_URL, CANTIDAD_CRIPTOMONEDAS, CANTIDAD_VELAS
from backend.utils.formatters import formato_numero_grande, formato_porcentaje, formato_valor_monetario

def obtener_datos_criptos_coingecko() -> list[dict]:
    """
    Obtiene y procesa datos de mercado desde la API de CoinGecko.

    Realiza una petición para obtener una lista de las principales criptomonedas,
    procesa la respuesta JSON, enriquece los datos con campos formateados para la UI,
    y finalmente guarda las cotizaciones en un archivo local.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada uno representa una
                    criptomoneda con datos brutos y formateados. Retorna una
                    lista vacía si ocurre un error.

    Side Effects:
        - Guarda los datos de cotizaciones en un archivo JSON local a través de
          `guardar_datos_cotizaciones()`.
        - Imprime logs en la consola sobre el estado de la petición.

    Example of a returned item:
        {
            'id': 1, 'nombre': 'Bitcoin', 'ticker': 'BTC', 'precio_usd': '65000.10',
            'precio_usd_formatted': '$65,000.10', 'market_cap_formatted': '$1.28T', ...
        }
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
            # Procesa cada criptomoneda de forma segura
            resultado.append({
                "id": i,
                "nombre": dato.get("name"),
                "ticker": dato.get('symbol', '').upper(),
                "logo": dato.get("image"),
                
                # Datos crudos convertidos a string para consistencia
                "precio_usd": str(Decimal(str(dato.get("current_price", 0)))),
                "1h_%": str(Decimal(str(dato.get("price_change_percentage_1h_in_currency", 0)))),
                "24h_%": str(Decimal(str(dato.get("price_change_percentage_24h_in_currency", 0)))),
                "7d_%": str(Decimal(str(dato.get("price_change_percentage_7d_in_currency", 0)))),
                "market_cap": str(Decimal(str(dato.get("market_cap", 0)))),
                "volumen_24h": str(Decimal(str(dato.get("total_volume", 0)))),
                "circulating_supply": str(Decimal(str(dato.get("circulating_supply", 0)))),

                # Datos pre-formateados para la UI
                "precio_usd_formatted": formato_valor_monetario(Decimal(str(dato.get("current_price", 0)))),
                "1h_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_1h_in_currency", 0)))),
                "24h_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_24h_in_currency", 0)))),
                "7d_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_7d_in_currency", 0)))),
                "market_cap_formatted": formato_numero_grande(Decimal(str(dato.get("market_cap", 0)))),
                "volumen_24h_formatted": formato_numero_grande(Decimal(str(dato.get("total_volume", 0)))),
                "circulating_supply_formatted": f"{Decimal(str(dato.get('circulating_supply', 0))):,.0f} {dato.get('symbol', '').upper()}"
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

    Args:
        ticker (str): El ticker de la criptomoneda (ej. "BTC").
        interval (str): El intervalo de tiempo para las velas (ej. "1h", "4h", "1d").

    Returns:
        list[dict]: Una lista de diccionarios, donde cada uno representa una vela
                    con datos OHLCV (Open, High, Low, Close, Volume). Retorna
                    una lista vacía si ocurre un error.

    Example of a returned item:
        {
            'time': 1622505600, 'open': '49000.00', 'high': '49500.00',
            'low': '48800.00', 'close': '49300.00', 'volume': '1234.56'
        }
    """
    # La API de Binance espera el par completo (ej. 'BTCUSDT')
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
        
        # Transforma la lista de listas de Binance a una lista de diccionarios
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