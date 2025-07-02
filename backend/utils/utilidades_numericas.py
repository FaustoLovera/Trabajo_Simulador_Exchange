"""Utilidades para la manipulación y formateo de valores numéricos.

Este módulo es fundamental para la integridad financiera de la aplicación.
Centraliza todas las operaciones con `Decimal` para garantizar la máxima
precisión y evitar los errores de punto flotante.

Se divide en dos categorías de funciones:
1.  **Lógica y Precisión**: Conversión segura a Decimal y cuantización.
2.  **Formato para UI**: Conversión de valores Decimal a strings legibles.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

import config


def a_decimal(valor: Any) -> Decimal:
    """Convierte de forma segura un valor de cualquier tipo a un objeto Decimal.

    Esta función actúa como un "sanitizador" de entradas. Si el valor es
    inválido o nulo, devuelve Decimal('0') en lugar de lanzar un error,
    asegurando la robustez de los cálculos.

    Args:
        valor (Any): El valor a convertir (puede ser str, int, float, etc.).

    Returns:
        Decimal: El valor convertido a Decimal, o Decimal('0') como fallback.
    """
    if valor is None:
        return Decimal("0")
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")

def cuantizar_cripto(valor: Decimal) -> Decimal:
    """Aplica la cuantización estándar para valores de criptomonedas.

    Asegura que todos los cálculos de criptoactivos usen una precisión
    uniforme, definida en `config.PRECISION_CRIPTOMONEDA`.

    Args:
        valor (Decimal): El valor a cuantizar.

    Returns:
        Decimal: El valor con la precisión estándar aplicada.
    """
    return valor.quantize(config.PRECISION_CRIPTOMONEDA)

def cuantizar_usd(valor: Decimal) -> Decimal:
    """Aplica la cuantización estándar para valores en USD.

    Asegura que todos los cálculos en USD usen una precisión uniforme,
    definida en `config.PRECISION_USD`.

    Args:
        valor (Decimal): El valor a cuantizar.

    Returns:
        Decimal: El valor con la precisión estándar aplicada.
    """
    return valor.quantize(config.PRECISION_USD)


# --- Funciones de Formateo para Presentación (Versión Final) ---

def formato_cantidad_cripto(valor: Decimal) -> str:
    """Formatea una cantidad de criptomoneda para su visualización.

    Convierte un valor Decimal a un string con separadores de miles y una
    precisión estándar, eliminando ceros decimales no significativos.
    Ej: Decimal('1234.56700000') -> "1,234.567"

    Args:
        valor (Decimal): La cantidad de criptomoneda a formatear.

    Returns:
        str: El valor formateado como string.
    """
    valor_q = cuantizar_cripto(valor)
    # El carácter "," es la clave para los separadores de miles.
    precision = abs(config.PRECISION_CRIPTOMONEDA.as_tuple().exponent)
    string_formateado = f"{valor_q:,.{precision}f}"
    
    if '.' in string_formateado:
        string_formateado = string_formateado.rstrip('0').rstrip('.')
        
    return string_formateado

def formato_cantidad_usd(valor: Decimal, simbolo: str = "$") -> str:
    """Formatea una cantidad en USD para su visualización.

    Convierte un valor Decimal a un string con un símbolo de moneda,
    separadores de miles y precisión estándar, eliminando ceros no
    significativos. Ej: Decimal('1234.50') -> "$1,234.5"

    Args:
        valor (Decimal): La cantidad en USD a formatear.
        simbolo (str, optional): Símbolo de moneda. Por defecto "$".

    Returns:
        str: El valor formateado como string.
    """
    valor_q = cuantizar_usd(valor)
    # El carácter "," es la clave para los separadores de miles.
    precision = abs(config.PRECISION_USD.as_tuple().exponent)
    string_formateado = f"{valor_q:,.{precision}f}"
    
    if '.' in string_formateado:
        string_formateado = string_formateado.rstrip('0').rstrip('.')
        
    return f"{simbolo}{string_formateado}"

def formato_numero_grande(valor: Decimal, simbolo: str = "$") -> str:
    """Formatea números grandes con sufijos de abreviatura (M, B, T).

    Simplifica la lectura de cifras muy grandes. Para valores menores a 1 millón,
    recurre a `formato_cantidad_usd` para un formato estándar.
    - 1,500,000 -> $1.50M
    - 2,500,000,000 -> $2.50B

    Args:
        valor (Decimal): El número a formatear.
        simbolo (str, optional): Símbolo de moneda. Por defecto "$".

    Returns:
        str: El número abreviado y formateado como string.
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
    """Formatea un número como un string de porcentaje con dos decimales.

    Ej: Decimal('25.1234') -> "25.12%"

    Args:
        valor (Decimal): El valor a formatear.

    Returns:
        str: El valor como string de porcentaje.
    """
    return f"{a_decimal(valor):.2f}%"