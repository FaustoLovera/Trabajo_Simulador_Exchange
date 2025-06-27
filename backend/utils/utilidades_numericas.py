# backend/utils/utilidades_numericas.py

"""
Módulo de Utilidades Numéricas.

Este módulo centraliza todas las operaciones relacionadas con la manipulación
de números en la aplicación, especialmente para garantizar la consistencia
y precisión al trabajar con la librería `Decimal`.
"""

from decimal import Decimal, InvalidOperation

from config import PRECISION_CRIPTOMONEDA, PRECISION_USD


def a_decimal(valor) -> Decimal:
    """
    Convierte de forma segura un valor a un objeto Decimal.
    """
    if valor is None:
        return Decimal("0")
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")

def cuantizar_cripto(valor: Decimal) -> Decimal:
    """
    Cuantiza un valor Decimal a la precisión estándar para criptomonedas.
    """
    return valor.quantize(PRECISION_CRIPTOMONEDA)

def cuantizar_usd(valor: Decimal) -> Decimal:
    """
    Cuantiza un valor Decimal a la precisión estándar para USD.
    """
    return valor.quantize(PRECISION_USD)


# --- Funciones de Formateo para Presentación (Versión Final) ---

def formato_cantidad_cripto(valor: Decimal) -> str:
    """
    Formatea una cantidad de criptomoneda con separadores de miles
    y elimina ceros decimales innecesarios.
    """
    valor_q = cuantizar_cripto(valor)
    # El carácter "," es la clave para los separadores de miles.
    precision = abs(PRECISION_CRIPTOMONEDA.as_tuple().exponent)
    string_formateado = f"{valor_q:,.{precision}f}"
    
    if '.' in string_formateado:
        string_formateado = string_formateado.rstrip('0').rstrip('.')
        
    return string_formateado

def formato_cantidad_usd(valor: Decimal, simbolo: str = "$") -> str:
    """
    Formatea un valor monetario en USD con separadores de miles
    y elimina ceros decimales innecesarios.
    """
    valor_q = cuantizar_usd(valor)
    # El carácter "," es la clave para los separadores de miles.
    precision = abs(PRECISION_USD.as_tuple().exponent)
    string_formateado = f"{valor_q:,.{precision}f}"
    
    if '.' in string_formateado:
        string_formateado = string_formateado.rstrip('0').rstrip('.')
        
    return f"{simbolo}{string_formateado}"

def formato_numero_grande(valor: Decimal, simbolo: str = "$") -> str:
    """
    Formatea números grandes con abreviaturas (M, B, T).
    Para números menores a 1 millón, usa el formato USD estándar.
    """
    numero = a_decimal(valor)

    if numero >= 1_000_000_000_000:
        return f"{simbolo}{(numero / Decimal('1e12')).quantize(Decimal('0.01'))}T"
    if numero >= 1_000_000_000:
        return f"{simbolo}{(numero / Decimal('1e9')).quantize(Decimal('0.01'))}B"
    if numero >= 1_000_000:
        return f"{simbolo}{(numero / Decimal('1e6')).quantize(Decimal('0.01'))}M"
    
    # Para números por debajo de 1 millón, usamos el formato USD con comas.
    return formato_cantidad_usd(numero, simbolo)

def formato_porcentaje(valor: Decimal) -> str:
    """
    Formatea un número como un porcentaje con dos decimales.
    """
    return f"{a_decimal(valor):.2f}%"