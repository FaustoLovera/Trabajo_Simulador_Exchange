import json

def obtener_tabla_criptos():
    with open("./datos/datos_cotizaciones.json") as f:
        datos = json.load(f)

    tabla = []
    for cripto in datos:
        fila = [
            cripto["id"],
            f"<img src='{cripto['logo']}' width='20'> {cripto['nombre']} ({cripto['ticker']})",
            round(cripto["precio_usd"], 2),
            round(cripto["1h_%"], 2),
            round(cripto["24h_%"], 2),
            round(cripto["7d_%"], 2),
            round(cripto["market_cap"] / 1e9, 2),  # en miles de millones
            round(cripto["volumen_24h"] / 1e6, 2),  # en millones
            round(cripto["circulating_supply"], 2)
        ]
        tabla.append(fila)

    return tabla
