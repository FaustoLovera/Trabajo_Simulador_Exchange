# backend/utils/formatters.py
from datetime import datetime
from decimal import Decimal

def formato_numero_grande(valor, simbolo="$"):
    """Formatea números grandes con abreviaturas y símbolo de moneda."""
    if not isinstance(valor, (int, float, Decimal)):
        return "-"
    num = Decimal(valor)
    
    if num >= 1_000_000_000_000:
        return f"{simbolo}{(num / Decimal('1e12')).quantize(Decimal('0.01'))}T"
    if num >= 1_000_000_000:
        return f"{simbolo}{(num / Decimal('1e9')).quantize(Decimal('0.01'))}B"
    if num >= 1_000_000:
        return f"{simbolo}{(num / Decimal('1e6')).quantize(Decimal('0.01'))}M"
    return f"{simbolo}{num:,.0f}"

def formato_porcentaje(valor):
    """Formatea un porcentaje con 2 decimales y el signo %."""
    if not isinstance(valor, (int, float, Decimal)):
        return "-%"
    return f"{Decimal(valor):.2f}%"

# ===> FUNCIÓN CORREGIDA <===
def formato_valor_monetario(valor, simbolo="$", decimales=2):
    """Formatea un valor como moneda con N decimales."""
    if not isinstance(valor, (int, float, Decimal)):
        return "-"
    # Usamos un f-string con una expresión para formatear dinámicamente los decimales
    return f"{simbolo}{Decimal(valor):,.{decimales}f}"

def formato_cantidad_cripto(valor, decimales=8):
    """Formatea una cantidad de cripto con N decimales."""
    if not isinstance(valor, (int, float, Decimal)):
        return "-"
    return f"{Decimal(valor):.{decimales}f}"

def formato_fecha_hora(timestamp):
    """Formatea un timestamp UNIX a un string de fecha y hora local."""
    if not isinstance(timestamp, (int, float)):
        return "--:--"
    try:
        # Convierte el timestamp a un objeto datetime
        dt_object = datetime.fromtimestamp(timestamp)
        # Formatea la fecha y la hora en un formato legible
        return dt_object.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return "--:--"