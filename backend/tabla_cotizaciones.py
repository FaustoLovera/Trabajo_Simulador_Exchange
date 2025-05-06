import json
from config import COTIZACIONES_PATH


def obtener_tabla_criptos():
    """
    Carga los datos de las criptomonedas desde el archivo de cotizaciones y
    genera una tabla con la información relevante de cada criptomoneda. La tabla incluye
    detalles como el nombre, ticker, precio en USD, variación en diferentes intervalos de tiempo
    (1 hora, 24 horas, 7 días), capitalización de mercado, volumen en las últimas 24 horas y
    suministro circulante.

    La función utiliza funciones adicionales para formatear y resaltar ciertos valores,
    como el precio y las variaciones porcentuales, y devuelve la tabla en forma de lista de listas.
    """

    with open(COTIZACIONES_PATH) as f:
        datos = json.load(f)

    tabla = [
        [
            cripto["id"],
            f"<img src='{cripto['logo']}' width='20' class='logo-cripto'> <span class='nombre-cripto'>{cripto['nombre']}</span> <span class='ticker-cripto'>({cripto['ticker']})</span>",
            envolver_variacion_coloreada(cripto["precio_usd"], con_signo_dolar=True),
            envolver_variacion_coloreada(cripto["1h_%"]),
            envolver_variacion_coloreada(cripto["24h_%"]),
            envolver_variacion_coloreada(cripto["7d_%"]),
            *map(
                formatear_numero,
                [
                    cripto["market_cap"],
                    cripto["volumen_24h"],
                    cripto["circulating_supply"],
                ],
            ),
        ]
        for cripto in datos
    ]

    return tabla


def envolver_variacion_coloreada(valor, con_signo_dolar=False):
    """
    Envuelve un valor numérico en un formato HTML estilizado, añadiendo clases CSS y
    flechas para representar variaciones positivas o negativas. Si `con_signo_dolar` es
    True, el valor será precedido por el signo de dólar ($) y se mostrará con formato
    monetario; de lo contrario, se mostrará el porcentaje con un símbolo de porcentaje (%).

    Dependiendo del signo del valor, se aplican diferentes clases CSS para resaltar las
    variaciones positivas (con clase "positivo") o negativas (con clase "negativo"),
    y se incluye una flecha verde (▲) para valores positivos y una flecha roja (▼) para valores negativos.

    El valor también se redondea a dos decimales y se presenta dentro de un `span`
    con las clases apropiadas para su visualización en una página web.
    """

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
    """
    Formatea un número grande para mostrarlo con un sufijo adecuado (T, B, M) según su magnitud
    o con una escala manual especificada. Si el número es menor que un millón, se muestra con
    dos decimales sin escala. Si se proporciona una escala manual (T, B, M), el número se ajusta
    a esa escala y se muestra con el sufijo correspondiente.

    - Si `n` es `None`, se devuelve un guion ("-").
    - Si `escala_manual` es especificado, el número se ajusta a la escala proporcionada
        y se muestra con la notación correspondiente.
    - Si no se proporciona `escala_manual`, el número se ajusta automáticamente
        según las escalas predefinidas (T para billones, B para mil millones y M para millones).
    """

    if n is None:
        return "-"

    if escala_manual:
        escalas = {"T": 1e12, "B": 1e9, "M": 1e6}
        return f"{n / escalas[escala_manual]:,.2f} {escala_manual}"

    for valor, simbolo in [(1e12, "T"), (1e9, "B"), (1e6, "M")]:
        if n >= valor:
            return f"{n / valor:,.2f} {simbolo}"
    return f"{n:.2f}"
