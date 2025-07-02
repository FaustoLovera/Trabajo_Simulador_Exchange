"""Utilidades para el formateo de datos en la interfaz de usuario.

Este módulo ofrece funciones de ayuda para convertir datos brutos (como fechas
o valores de rendimiento) en formatos legibles y con estilo para la vista.
"""

from datetime import datetime
from decimal import Decimal
from typing import Union


def get_performance_indicator(value: Union[str, Decimal]) -> dict:
    """Genera datos de estilo para un indicador de rendimiento (positivo/negativo).

    Analiza un valor numérico para determinar si es positivo o negativo y
    devuelve un diccionario con una clase CSS y un símbolo de flecha, ideal
    para la renderización en la interfaz de usuario.

    Args:
        value (Union[str, Decimal]): El valor de rendimiento a analizar.

    Returns:
        dict: Un diccionario con 'className' ('positivo' o 'negativo') y
              'arrow' ('▲' o '▼'). Devuelve valores vacíos si la entrada
              no es un número válido.
    """
    try:
        valor_decimal = Decimal(str(value))
        if valor_decimal >= 0:
            return {"className": "positivo", "arrow": "▲"}
        return {"className": "negativo", "arrow": "▼"}
    except (ValueError, TypeError, InvalidOperation):
        return {"className": "", "arrow": ""}


def format_datetime(timestamp: Union[int, float, str]) -> str:
    """Convierte un timestamp o un string ISO a un formato de fecha legible.

    Acepta timestamps numéricos (segundos desde la época) o strings en formato
    ISO 8601 y los convierte a un formato local estándar 'dd/mm/YYYY HH:MM:SS'.

    Args:
        timestamp: El valor de fecha/hora a formatear.

    Returns:
        str: La fecha y hora formateada. Devuelve '--:--' si la entrada
             es inválida o nula.
    """
    if not timestamp:
        return "--:--"
    
    try:
        if isinstance(timestamp, (int, float)):
            dt_object = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            dt_object = datetime.fromisoformat(timestamp)
        else:
            return "--:--"
            
        return dt_object.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return "--:--"