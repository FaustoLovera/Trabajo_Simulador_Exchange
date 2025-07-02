"""Pruebas Unitarias para las Utilidades Numéricas.

Este archivo contiene pruebas para las funciones auxiliares del módulo
`utils.utilidades_numericas`. Estas funciones son cruciales para mantener la
precisión en los cálculos financieros y para formatear los números de una
manera consistente y legible para el usuario final.

Las pruebas cubren tres áreas principales:
1.  **Conversión Segura**: La función `a_decimal` se prueba para asegurar que
    convierte robustamente varios tipos de datos a `Decimal`, manejando
    errores de forma predecible.
2.  **Cuantización**: Se prueban `cuantizar_cripto` y `cuantizar_usd` para
    verificar que aplican la precisión decimal correcta para cada tipo de activo.
3.  **Formateo**: Se validan las funciones de formato (`formato_cantidad_*`)
    que preparan los números para ser mostrados en la interfaz de usuario.
"""

import pytest
from decimal import Decimal
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto, cuantizar_usd

# --- Tests para a_decimal ---

def test_a_decimal_debe_convertir_string_numerico_a_decimal():
    """Verifica que un string numérico se convierte correctamente a Decimal."""
    assert a_decimal("123.45") == Decimal("123.45")

def test_a_decimal_debe_convertir_entero_a_decimal():
    """Verifica que un número entero se convierte correctamente a Decimal."""
    assert a_decimal(123) == Decimal("123")

def test_a_decimal_debe_convertir_flotante_a_decimal():
    """Verifica que un número de punto flotante se convierte correctamente a Decimal."""
    assert a_decimal(123.45) == Decimal("123.45")

def test_a_decimal_debe_convertir_none_a_decimal_cero():
    """Verifica que None se convierte de forma segura a Decimal('0')."""
    assert a_decimal(None) == Decimal("0")

def test_a_decimal_debe_convertir_string_no_numerico_a_decimal_cero():
    """Verifica que un string no numérico se convierte de forma segura a Decimal('0')."""
    assert a_decimal("hola") == Decimal("0")

# --- Tests para cuantizar_cripto ---

def test_cuantizar_cripto_debe_redondear_a_ocho_decimales():
    """Verifica que `cuantizar_cripto` redondea a 8 decimales, estándar para cripto."""
    valor = Decimal("0.123456789")
    assert cuantizar_cripto(valor) == Decimal("0.12345679")

# --- Tests para cuantizar_usd ---

def test_cuantizar_usd_debe_redondear_a_cuatro_decimales():
    """Verifica que `cuantizar_usd` redondea a 4 decimales, útil para precios."""
    valor = Decimal("123.45678")
    assert cuantizar_usd(valor) == Decimal("123.4568")

# --- Tests para formato_cantidad_cripto ---

def test_formato_cantidad_cripto_debe_aplicar_separador_de_miles_a_entero():
    """Verifica el formateo de un número entero con separadores de miles."""
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('10000')) == "10,000"

def test_formato_cantidad_cripto_debe_aplicar_separador_de_miles_a_decimal():
    """Verifica el formateo de un número decimal con separadores de miles."""
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('12345.67')) == "12,345.67"

def test_formato_cantidad_cripto_debe_eliminar_ceros_decimales_no_significativos():
    """Verifica que el formateo elimina los ceros decimales no significativos."""
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('12.1200')) == "12.12"

# --- Tests para formato_cantidad_usd ---

def test_formato_cantidad_usd_debe_incluir_simbolo_dolar_y_separadores():
    """Verifica el formateo de un valor monetario en USD, incluyendo el símbolo '$'."""
    from backend.utils.utilidades_numericas import formato_cantidad_usd
    assert formato_cantidad_usd(Decimal('12345.67')) == "$12,345.67"

def test_formato_cantidad_usd_debe_eliminar_ceros_decimales_no_significativos():
    """Verifica la eliminación de ceros no significativos en el formato USD."""
    from backend.utils.utilidades_numericas import formato_cantidad_usd
    assert formato_cantidad_usd(Decimal('10.1000')) == "$10.1"

# --- Tests para formato_numero_grande ---

def test_formato_numero_grande_debe_abreviar_con_M_cuando_es_millon():
    """Verifica que un número grande (millones) se abrevia con la letra 'M'."""
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('1500000')) == "$1.50M"

def test_formato_numero_grande_debe_abreviar_con_B_cuando_es_billon():
    """
    Prueba que un valor en miles de millones se formatea con 'B'.
    """
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('2500000000')) == "$2.50B"

def test_formato_numero_grande_debe_usar_formato_estandar_cuando_es_menor_a_un_millon():
    """
    Prueba que un valor menor a un millón usa el formato de formato_cantidad_usd.
    """
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('1234.56')) == "$1,234.56"
