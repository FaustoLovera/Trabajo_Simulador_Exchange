"""
Módulo de Utilidades Numéricas.

Este módulo centraliza todas las operaciones relacionadas con la manipulación
de números en la aplicación, especialmente para garantizar la consistencia
y precisión al trabajar con la librería `Decimal`.

Funciones:
- Conversión segura a `Decimal`.
- Cuantización a precisiones estándar (cripto, USD).
- Formateo para presentación en el frontend.
"""

from decimal import Decimal, InvalidOperation

from config import PRECISION_CRIPTOMONEDA, PRECISION_USD


def a_decimal(valor) -> Decimal:
    """
    Convierte de forma segura un valor a un objeto Decimal.

    Maneja diferentes tipos de entrada (int, float, str, None) y valores
    inválidos, devolviendo siempre Decimal('0') en caso de error o entrada nula.

    Args:
        valor: El valor a convertir.

    Returns:
        Un objeto Decimal.
    """
    if valor is None:
        return Decimal("0")
    try:
        # Convertir a string primero es la forma más segura de crear un Decimal,
        # especialmente desde un float, para evitar imprecisiones binarias.
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")

def cuantizar_cripto(valor: Decimal) -> Decimal:
    """
    Cuantiza un valor Decimal a la precisión estándar para criptomonedas.

    Args:
        valor: El objeto Decimal a cuantizar.

    Returns:
        El valor Decimal cuantizado a 8 decimales.
    """
    return valor.quantize(PRECISION_CRIPTOMONEDA)

def cuantizar_usd(valor: Decimal) -> Decimal:
    """
    Cuantiza un valor Decimal a la precisión estándar para USD.

    Args:
        valor: El objeto Decimal a cuantizar.

    Returns:
        El valor Decimal cuantizado a 2 o 4 decimales, según config.
    """
    return valor.quantize(PRECISION_USD)


# --- Funciones de Formateo para Presentación ---

def formato_cantidad_cripto(valor: Decimal) -> str:
    """
    Formatea una cantidad de criptomoneda como string con 8 decimales.

    Args:
        valor (Decimal): La cantidad a formatear.

    Returns:
        La cantidad formateada como string. Ej: "0.12345678".
    """
    return f"{cuantizar_cripto(valor):.8f}"

def formato_cantidad_usd(valor: Decimal, simbolo: str = "$") -> str:
    """
    Formatea un valor monetario en USD con 2 decimales y separadores de miles.

    Args:
        valor (Decimal): El valor a formatear.
        simbolo (str, optional): Símbolo de la moneda. Por defecto es "$".

    Returns:
        El valor formateado. Ej: "$1,234.56".
    """
    # La cantidad de decimales en la f-string debe coincidir con la precisión en config.py
    # Decimal('0.0001'), usa .4f.
    decimales = abs(PRECISION_USD.as_tuple().exponent)
    return f"{simbolo}{cuantizar_usd(valor):,.{decimales}f}"

def formato_numero_grande(valor: Decimal, simbolo: str = "$") -> str:
    """
    Formatea números grandes con abreviaturas (M, B, T).

    Args:
        valor (Decimal): El número a formatear.
        simbolo (str, optional): Símbolo a prefijar. Por defecto es "$".

    Returns:
        El número formateado como string. Ej: "$1.25M", "$2.5B".
    """
    numero = a_decimal(valor)

    if numero >= 1_000_000_000_000:
        return f"{simbolo}{(numero / Decimal('1e12')).quantize(Decimal('0.01'))}T"
    if numero >= 1_000_000_000:
        return f"{simbolo}{(numero / Decimal('1e9')).quantize(Decimal('0.01'))}B"
    if numero >= 1_000_000:
        return f"{simbolo}{(numero / Decimal('1e6')).quantize(Decimal('0.01'))}M"
    return f"{simbolo}{numero:,.0f}"

def formato_porcentaje(valor: Decimal) -> str:
    """
    Formatea un número como un porcentaje con dos decimales.

    Args:
        valor (Decimal): El número a formatear.

    Returns:
        El número como string de porcentaje. Ej: "25.45%".
    """
    return f"{a_decimal(valor):.2f}%"