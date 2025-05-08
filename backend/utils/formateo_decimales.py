def formato_valor(valor, decimales=2, umbral=0.0001, simbolo="$"):
    try:
        val = float(valor)
        if 0 < abs(val) < umbral:
            return f"&lt; {simbolo}{umbral:.{decimales}f}"
        return f"{simbolo}{val:.{decimales}f}"
    except (TypeError, ValueError):
        return "-"

def formato_cantidad(valor, decimales=8, umbral=0.00000001):
    try:
        val = float(valor)
        if 0 < abs(val) < umbral:
            return f"&lt; {umbral:.{decimales}f}"
        return f"{val:.{decimales}f}"
    except (TypeError, ValueError):
        return "-"

def registrar_filtros(app):
    app.jinja_env.filters["formato_valor"] = formato_valor
    app.jinja_env.filters["formato_cantidad"] = formato_cantidad