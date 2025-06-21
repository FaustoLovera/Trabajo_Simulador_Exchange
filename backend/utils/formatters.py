# backend/utils/formatters.py
"""
Utilidades de formateo para la presentación de datos.

Este módulo proporciona un conjunto de funciones reutilizables para dar formato a
diversos tipos de datos (monetarios, porcentajes, fechas) de una manera
consistente y legible para el usuario final.
"""

from datetime import datetime
from decimal import Decimal
from typing import Union

# Alias de tipo para valores numéricos que pueden ser procesados.
Numeric = Union[int, float, Decimal]

def formato_numero_grande(valor: Numeric, simbolo: str = "$") -> str:
    """
    Formatea números grandes con abreviaturas (M, B, T) y un símbolo.

    Args:
        valor (Numeric): El número a formatear.
        simbolo (str, optional): Símbolo a prefijar. Por defecto es "$".

    Returns:
        str: El número formateado como string. Ej: "$1.25M", "$2.5B".
    """
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

def formato_porcentaje(valor: Numeric) -> str:
    """
    Formatea un número como un porcentaje con dos decimales.

    Args:
        valor (Numeric): El número a formatear.

    Returns:
        str: El número como string de porcentaje. Ej: "25.45%".
    """
    if not isinstance(valor, (int, float, Decimal)):
        return "-%"
    return f"{Decimal(valor):.2f}%"

def formato_valor_monetario(valor: Numeric, simbolo: str = "$", decimales: int = 2) -> str:
    """
    Formatea un valor numérico como una cadena de texto monetaria.

    Args:
        valor (Numeric): El valor a formatear.
        simbolo (str, optional): Símbolo de la moneda. Por defecto es "$".
        decimales (int, optional): Número de decimales a mostrar. Por defecto es 2.

    Returns:
        str: El valor formateado. Ej: "$1,234.56".
    """
    if not isinstance(valor, (int, float, Decimal)):
        return "-"
    return f"{simbolo}{Decimal(valor):,.{decimales}f}"

def formato_cantidad_cripto(valor: Numeric, decimales: int = 8) -> str:
    """
    Formatea una cantidad de criptomoneda con una precisión específica.

    Args:
        valor (Numeric): La cantidad a formatear.
        decimales (int, optional): Número de decimales. Por defecto es 8.

    Returns:
        str: La cantidad formateada. Ej: "0.12345678".
    """
    if not isinstance(valor, (int, float, Decimal)):
        return "-"
    return f"{Decimal(valor):.{decimales}f}"

def formato_fecha_hora(timestamp: Union[int, float, str]) -> str:
    """
    Formatea un timestamp o un string ISO a una fecha y hora local.

    Maneja tanto timestamps numéricos (segundos desde la época) como strings
    de fecha en formato ISO 8601.

    Args:
        timestamp (Union[int, float, str]): El timestamp o string a formatear.

    Returns:
        str: La fecha y hora formateada. Ej: "21 Jun 2024, 15:45".
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