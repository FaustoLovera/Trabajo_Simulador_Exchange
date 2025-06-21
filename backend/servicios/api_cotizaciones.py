from decimal import Decimal
import requests
from backend.servicios.velas_logica import guardar_datos_cotizaciones, guardar_datos_velas
from config import COINGECKO_URL, BINANCE_URL, CANTIDAD_CRIPTOMONEDAS, CANTIDAD_VELAS
from backend.utils.formatters import formato_numero_grande, formato_porcentaje, formato_valor_monetario

def obtener_datos_criptos_coingecko():
    """
    Obtiene información del mercado de criptomonedas desde la API pública de CoinGecko.
    Añade campos formateados para que la UI pueda renderizarlos directamente.
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
        respuesta = requests.get(COINGECKO_URL, params)
        respuesta.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de CoinGecko: {str(e)}")
        return []

    print(f"✅ Estado de la respuesta CoinGecko: {respuesta.status_code}")

    try:
        datos = respuesta.json()
        resultado = [
            {
                "id": i,
                "nombre": dato.get("name"),
                "ticker": dato.get('symbol', '').upper(),
                "logo": dato.get("image"),
                
                # Datos crudos
                "precio_usd": str(Decimal(str(dato.get("current_price", 0)))),
                "1h_%": str(Decimal(str(dato.get("price_change_percentage_1h_in_currency", 0)))),
                "24h_%": str(Decimal(str(dato.get("price_change_percentage_24h_in_currency", 0)))),
                "7d_%": str(Decimal(str(dato.get("price_change_percentage_7d_in_currency", 0)))),
                "market_cap": str(Decimal(str(dato.get("market_cap", 0)))),
                "volumen_24h": str(Decimal(str(dato.get("total_volume", 0)))),
                "circulating_supply": str(Decimal(str(dato.get("circulating_supply", 0)))),

                # Datos pre-formateados para la UI
                "precio_usd_formatted": formato_valor_monetario(Decimal(str(dato.get("current_price", 0))), decimales=2),
                "1h_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_1h_in_currency", 0)))),
                "24h_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_24h_in_currency", 0)))),
                "7d_%_formatted": formato_porcentaje(Decimal(str(dato.get("price_change_percentage_7d_in_currency", 0)))),
                "market_cap_formatted": formato_numero_grande(Decimal(str(dato.get("market_cap", 0)))),
                "volumen_24h_formatted": formato_numero_grande(Decimal(str(dato.get("total_volume", 0)))),
                "circulating_supply_formatted": f"{Decimal(str(dato.get('circulating_supply', 0))):,.0f} {dato.get('symbol', '').upper()}"
            }
            for i, dato in enumerate(datos, start=1)
        ]
    except (KeyError, TypeError, ValueError) as e:
        print(f"❌ Error al procesar los datos de CoinGecko: {str(e)}")
        return []

    print(f"💡 Total de criptos procesadas: {len(resultado)}")
    guardar_datos_cotizaciones(resultado)
    return resultado


def obtener_velas_binance():
    """
    Obtiene datos históricos de velas (Klines) diarias del par BTC/USDT.
    """
    params = {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "limit": CANTIDAD_VELAS,
    }
    try:
        respuesta = requests.get(BINANCE_URL, params)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de Binance: {str(e)}")
        return []

    print(f"✅ Estado de la respuesta Binance: {respuesta.status_code}")

    datos = respuesta.json()
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
    
    print(f"💡 Total de velas procesadas: {len(resultado)}")
    guardar_datos_velas(resultado)
    return resultado