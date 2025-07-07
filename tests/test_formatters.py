"""
Pruebas Unitarias para las Utilidades de Formateo.

Este archivo contiene pruebas para las funciones auxiliares del módulo
`backend.utils.formatters`. Estas funciones son cruciales para la capa de
presentación, asegurando que los datos se muestren al usuario de una manera
consistente y legible.
"""

import pytest
from decimal import Decimal
from datetime import datetime

# Importar las funciones a probar
from backend.utils.formatters import get_performance_indicator, format_datetime

# --- Tests para get_performance_indicator ---

@pytest.mark.parametrize("valor_entrada, clase_esperada, flecha_esperada", [
    # Casos positivos
    (Decimal("5.2"), "positivo", "▲"),
    (Decimal("0.0"), "positivo", "▲"), # Cero se considera no negativo
    ("100", "positivo", "▲"),
    
    # Casos negativos
    (Decimal("-3.7"), "negativo", "▼"),
    ("-0.001", "negativo", "▼"),

    # Casos de borde y erróneos
    (None, "", ""),
    ("texto", "", ""),
    ("", "", "")
])
def test_get_performance_indicator(valor_entrada, clase_esperada, flecha_esperada):
    """
    Verifica que el indicador de rendimiento genere la clase CSS y la flecha
    correctas para valores positivos, negativos y de borde.
    """
    resultado = get_performance_indicator(valor_entrada)
    assert resultado["className"] == clase_esperada
    assert resultado["arrow"] == flecha_esperada


# --- Tests para format_datetime ---

def test_format_datetime_con_timestamp_iso():
    """Verifica el formateo de una fecha a partir de un string ISO 8601."""
    timestamp_iso = "2025-07-15T22:30:55"
    resultado_esperado = "15/07/2025 22:30:55"
    assert format_datetime(timestamp_iso) == resultado_esperado

def test_format_datetime_con_timestamp_numerico():
    """Verifica el formateo de una fecha a partir de un timestamp numérico (epoch)."""
    # El timestamp 1672531200 corresponde a 2023-01-01 00:00:00 UTC
    timestamp_num = 1672531200
    # El resultado dependerá de la zona horaria del sistema, pero el formato debe ser correcto.
    # Para hacerlo independiente de la zona horaria, podríamos usar objetos de fecha con tzinfo,
    # pero para este caso, verificamos que el formato es el esperado.
    # Asumimos que strftime funciona correctamente y solo probamos el formato.
    dt_object = datetime.fromtimestamp(timestamp_num)
    resultado_esperado = dt_object.strftime("%d/%m/%Y %H:%M:%S")
    assert format_datetime(timestamp_num) == resultado_esperado

def test_format_datetime_con_entrada_invalida():
    """Verifica que devuelve un valor de fallback para entradas inválidas."""
    assert format_datetime(None) == "--:--"
    assert format_datetime("fecha invalida") == "--:--"
    assert format_datetime("") == "--:--"
    assert format_datetime(1j) == "--:--" # Un número complejo