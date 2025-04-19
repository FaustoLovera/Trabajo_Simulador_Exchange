import requests
from guardar_datos_cotizaciones import guardar_datos_cotizaciones, guardar_datos_velas

URL = "https://api.coingecko.com/api/v3/coins/markets"

def obtener_datos_criptos_coingecko():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }

    r = requests.get(URL, params=params)
    print(f"Estado de la respuesta: {r.status_code}")
    if r.status_code != 200:
        print("❌ Error al obtener datos de CoinGecko")
        return {"error": "No se pudo obtener los datos"}

    datos = r.json()
    # print(f"💡 Datos obtenidos: {datos}")
    resultado = []

    for i, cripto in enumerate(datos, start=1):
        
        if isinstance(cripto, dict):
            resultado.append({
                "id": i,
                "nombre": cripto.get("name"),
                "ticker": cripto.get("symbol").upper(),
                "logo": cripto.get("image"),
                "precio_usd": cripto.get("current_price"),
                "1h_%": cripto.get("price_change_percentage_1h_in_currency"),
                "24h_%": cripto.get("price_change_percentage_24h_in_currency"),
                "7d_%": cripto.get("price_change_percentage_7d_in_currency"),
                "market_cap": cripto.get("market_cap"),
                "volumen_24h": cripto.get("total_volume"),
                "circulating_supply": cripto.get("circulating_supply")
            })
        else:
            print(f"Advertencia: El dato para la cripto en la posición {i} no es un diccionario. Valor recibido: {cripto}")

    print(f"💡 Total de criptos procesadas: {len(resultado)}")
    guardar_datos_cotizaciones(resultado)
    return resultado

def obtener_velas_binance():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "limit": 350
    }

    r = requests.get(url, params=params)
    print(f"Estado de la respuesta Binance: {r.status_code}")
    if r.status_code != 200:
        print("❌ Error al obtener datos de Binance")
        return {"error": "No se pudo obtener los datos"}

    datos = r.json()
    resultado = []

    for vela in datos:
        resultado.append({
            "time": int(vela[0] / 1000),  # timestamp en segundos
            "open": float(vela[1]),
            "high": float(vela[2]),
            "low": float(vela[3]),
            "close": float(vela[4]),
            "volume": float(vela[5])
        })

    print(f"💡 Total de velas procesadas: {len(resultado)}")
    guardar_datos_velas(resultado)
    return resultado
