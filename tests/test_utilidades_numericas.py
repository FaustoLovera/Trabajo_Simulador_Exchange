import pytest
from decimal import Decimal
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto, cuantizar_usd

# --- Tests para a_decimal ---

def test_a_decimal_str():
    """
    Prueba que convierte un string válido a Decimal.
    """
    assert a_decimal("123.45") == Decimal("123.45")

def test_a_decimal_int():
    """
    Prueba que convierte un int a Decimal.
    """
    assert a_decimal(123) == Decimal("123")

def test_a_decimal_float():
    """
    Prueba que convierte un float a Decimal.
    """
    assert a_decimal(123.45) == Decimal("123.45")

def test_a_decimal_none():
    """
    Prueba que None devuelve Decimal('0').
    """
    assert a_decimal(None) == Decimal("0")

def test_a_decimal_invalid_str():
    """
    Prueba que un string inválido devuelve Decimal('0').
    """
    assert a_decimal("hola") == Decimal("0")

# --- Tests para cuantizar_cripto ---

def test_cuantizar_cripto_redondeo():
    """
    Prueba que cuantizar_cripto redondea correctamente a 8 decimales.
    """
    valor = Decimal("0.123456789")
    assert cuantizar_cripto(valor) == Decimal("0.12345679")

# --- Tests para cuantizar_usd ---

def test_cuantizar_usd_redondeo():
    """
    Prueba que cuantizar_usd redondea correctamente a 4 decimales.
    """
    valor = Decimal("123.45678")
    assert cuantizar_usd(valor) == Decimal("123.4568")

# --- Tests para formato_cantidad_cripto ---

def test_formato_cantidad_cripto_entero():
    """
    Prueba que un número entero se formatea correctamente con separador de miles.
    """
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('10000')) == "10,000"

def test_formato_cantidad_cripto_decimales():
    """
    Prueba que un número con decimales se formatea correctamente.
    """
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('12345.67')) == "12,345.67"

def test_formato_cantidad_cripto_elimina_ceros():
    """
    Prueba que elimina ceros decimales sobrantes.
    """
    from backend.utils.utilidades_numericas import formato_cantidad_cripto
    assert formato_cantidad_cripto(Decimal('12.1200')) == "12.12"

# --- Tests para formato_cantidad_usd ---

def test_formato_cantidad_usd_basico():
    """
    Prueba que un valor se formatea como USD con símbolo y formato correcto.
    """
    from backend.utils.utilidades_numericas import formato_cantidad_usd
    assert formato_cantidad_usd(Decimal('12345.67')) == "$12,345.67"

def test_formato_cantidad_usd_elimina_ceros():
    """
    Prueba que elimina ceros decimales sobrantes en USD.
    """
    from backend.utils.utilidades_numericas import formato_cantidad_usd
    assert formato_cantidad_usd(Decimal('10.1000')) == "$10.1"

# --- Tests para formato_numero_grande ---

def test_formato_numero_grande_millon():
    """
    Prueba que un valor en millones se formatea con 'M'.
    """
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('1500000')) == "$1.50M"

def test_formato_numero_grande_billones():
    """
    Prueba que un valor en miles de millones se formatea con 'B'.
    """
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('2500000000')) == "$2.50B"

def test_formato_numero_grande_menor_millon():
    """
    Prueba que un valor menor a un millón usa el formato de formato_cantidad_usd.
    """
    from backend.utils.utilidades_numericas import formato_numero_grande
    assert formato_numero_grande(Decimal('1234.56')) == "$1,234.56"
