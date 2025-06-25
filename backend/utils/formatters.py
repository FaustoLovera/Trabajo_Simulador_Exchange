# backend/utils/formatters.py
### MODIFICADO ###
"""
Utilidades de formateo para la presentación de datos no numéricos.

Este módulo proporciona un conjunto de funciones reutilizables para dar formato a
diversos tipos de datos como fechas y otros indicadores de UI.
La lógica de formateo numérico se ha movido a `utils.number_utils`.
"""

from datetime import datetime
from decimal import Decimal
from typing import Union

# Los formateadores numéricos se han movido a number_utils,
# pero aún podemos necesitar esta función para los indicadores de rendimiento.
def get_performance_indicator(value: Union[str, Decimal]) -> dict:
    """
    Analiza un valor de rendimiento y devuelve un diccionario con la clase CSS y
    el símbolo de flecha correspondiente.

    Args:
        value (Union[str, Decimal]): El valor de rendimiento.

    Returns:
        dict: Un diccionario con las claves 'className' y 'arrow'.
    """
    try:
        # Se usa to_decimal de number_utils para consistencia, aunque aquí no lo importamos
        # para mantener los módulos lo más desacoplados posible. La conversión simple funciona.
        valor_decimal = Decimal(str(value))
        if valor_decimal >= 0:
            return {"className": "positivo", "arrow": "▲"}
        return {"className": "negativo", "arrow": "▼"}
    except (ValueError, TypeError, InvalidOperation):
        return {"className": "", "arrow": ""}


def format_datetime(timestamp: Union[int, float, str]) -> str:
    """
    Formatea un timestamp o un string ISO a una fecha y hora local.

    Maneja tanto timestamps numéricos (segundos desde la época) como strings
    de fecha en formato ISO 8601.

    Args:
        timestamp: El timestamp o string a formatear.

    Returns:
        La fecha y hora formateada. Ej: "21/06/2024 15:45:12".
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