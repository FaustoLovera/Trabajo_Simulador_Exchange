import json


def obtener_tabla_criptos():
    with open("./datos/datos_cotizaciones.json") as f:
        datos = json.load(f)

    tabla = []
    for cripto in datos:
        fila = [
            cripto["id"],
            f"<img src='{cripto['logo']}' width='20' class='logo-cripto'> <span class='nombre-cripto'>{cripto['nombre']}</span> <span class='ticker-cripto'>({cripto['ticker']})</span>",
            envolver_variacion_coloreada(cripto["precio_usd"], con_signo_dolar=True),
            envolver_variacion_coloreada(cripto['1h_%']),
            envolver_variacion_coloreada(cripto['24h_%']),
            envolver_variacion_coloreada(cripto['7d_%']),
            formatear_numero(cripto["market_cap"]),
            formatear_numero(cripto["volumen_24h"]),
            formatear_numero(cripto["circulating_supply"]),
        ]
        tabla.append(fila)

        # print(tabla)

    return tabla


def envolver_variacion_coloreada(valor, con_signo_dolar=False):
    if valor > 0:
        clase = "positivo"
        if con_signo_dolar:
            sufijo = "$ "
        else:
            sufijo = " %"
    else:
        clase = "negativo"
        if con_signo_dolar:
            sufijo = "-$ "
        else:
            sufijo = "% "
    flecha = ""
    if not con_signo_dolar:
        if valor > 0:
            flecha = "<span class='flecha-verde'>▲</span>"
        else:
            flecha = "<span class='flecha-roja'>▼</span>"
    
    valor_redondeado = f"{valor:,.2f}"
    
    if con_signo_dolar:
        contenido = f"{sufijo}{valor_redondeado}"
    else:
        contenido = f"{valor_redondeado}{sufijo}"

    return f"<span class='{clase}'>{flecha} {contenido}</span>"


def formatear_numero(n, escala_manual=None):
    if n is None:
        return "-"

    if escala_manual:
        escalas = {"T": 1e12, "B": 1e9, "M": 1e6}
        return f"{n / escalas[escala_manual]:,.2f} {escala_manual}"

    for valor, simbolo in [(1e12, "T"), (1e9, "B"), (1e6, "M")]:
        if n >= valor:
            return f"{n / valor:,.2f} {simbolo}"
    return f"{n:.2f}"
