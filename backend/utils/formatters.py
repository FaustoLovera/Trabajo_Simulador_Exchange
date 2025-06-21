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
    """
    Formatea un timestamp a un string de fecha y hora local.
    CORRECCIÓN: Ahora maneja timestamps numéricos y strings de fecha ISO.
    """
    if not timestamp:
        return "--:--"
    
    try:
        if isinstance(timestamp, (int, float)):
            # Si es un número, lo trata como timestamp de Unix
            dt_object = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            # Si es un string, intenta parsearlo como formato ISO
            # El formato recibido del backend es ISO 8601, ej: "2025-06-21T16:57:31.123456"
            dt_object = datetime.fromisoformat(timestamp)
        else:
            # Si no es ni número ni string, no se puede formatear
            return "--:--"
            
        # Formatea la fecha y la hora en un formato legible (DD/MM/YYYY HH:MM:SS)
        return dt_object.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        # Captura cualquier error durante la conversión (ej. string mal formado)
        return "--:--"