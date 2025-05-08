from decimal import Decimal
import json
from config import COTIZACIONES_PATH


def obtener_todas_las_cotizaciones():
    try:
        with open(COTIZACIONES_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def envolver_variacion_coloreada(valor, con_signo_dolar=False):
    clase = "positivo" if valor > 0 else "negativo"
    sufijo = (
        (lambda v: "$ " if v > 0 else "-$ ")(valor)
        if con_signo_dolar
        else (lambda v: " %" if v > 0 else "% ")(valor)
    )
    flecha = (
        (
            "<span class='flecha-verde'>▲</span>"
            if valor > 0
            else "<span class='flecha-roja'>▼</span>"
        )
        if not con_signo_dolar
        else ""
    )

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


def obtener_tabla_criptos():
    from config import COTIZACIONES_PATH

    with open(COTIZACIONES_PATH) as f:
        datos = json.load(f)

    tabla = [
        [
            cripto["id"],
            f"<img src='{cripto['logo']}' width='20' class='logo-cripto'> <span class='nombre-cripto'>{cripto['nombre']}</span> <span class='ticker-cripto'>({cripto['ticker']})</span>",
            envolver_variacion_coloreada(Decimal(str(cripto["precio_usd"])), con_signo_dolar=True),
            envolver_variacion_coloreada(Decimal(str(cripto["1h_%"]))),
            envolver_variacion_coloreada(Decimal(str(cripto["24h_%"]))),
            envolver_variacion_coloreada(Decimal(str(cripto["7d_%"]))),
            *map(
                formatear_numero,
                [
                    Decimal(str(cripto["market_cap"])),
                    Decimal(str(cripto["volumen_24h"])),
                    Decimal(str(cripto["circulating_supply"])),
                ],
            ),
        ]
        for cripto in datos
    ]

    return tabla
