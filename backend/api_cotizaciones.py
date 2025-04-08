import requests

def obtener_datos_criptos_coingecko():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return {"error": "No se pudo obtener los datos"}

    datos = r.json()
    resultado = []

    for i, cripto in enumerate(datos, start=1):
        resultado.append({
            "id": i,
            "nombre": cripto.get("name"),
            "ticker": cripto.get("symbol").upper(),
            "precio_usd": cripto.get("current_price"),
            "1h_%": cripto.get("price_change_percentage_1h_in_currency"),
            "24h_%": cripto.get("price_change_percentage_24h_in_currency"),
            "7d_%": cripto.get("price_change_percentage_7d_in_currency"),
            "market_cap": cripto.get("market_cap"),
            "volumen_24h": cripto.get("total_volume"),
            "circulating_supply": cripto.get("circulating_supply")
        })
    
    # print(resultado)

    return resultado