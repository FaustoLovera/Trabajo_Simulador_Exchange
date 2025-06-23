import pytest
from decimal import Decimal, getcontext
from typing import Tuple

# Aseguramos la precisión para los cálculos con Decimal, es una buena práctica
getcontext().prec = 28

# Importamos la función que vamos a testear (con el guion bajo)
from backend.servicios.trading_logica import _calcular_detalles_swap


# --- Tests para Casos de Éxito ---

def test_compra_ingresando_monto_cripto():
    """
    Prueba una compra donde se especifica la cantidad de cripto a RECIBIR.
    Ejemplo: Quiero comprar exactamente 0.02 BTC.
    """
    exito, detalles = _calcular_detalles_swap(
        accion='comprar',
        modo_ingreso='monto',  # El usuario ingresa la cantidad de cripto
        monto_form=Decimal('0.02'),
        precio_origen_usdt=Decimal('1'),      # Precio de USDT
        precio_destino_usdt=Decimal('50000')  # Precio de BTC
    )
    
    assert exito is True
    assert detalles == {
        'origen': Decimal('1000.0'),  # Costará 1000 USDT
        'destino': Decimal('0.02'),   # Para recibir 0.02 BTC
        'valor_usd': Decimal('1000.0')
    }

def test_compra_ingresando_total_fiat():
    """
    Prueba una compra donde se especifica la cantidad de fiat a GASTAR.
    Ejemplo: Quiero gastar exactamente 1000 USDT en BTC.
    """
    exito, detalles = _calcular_detalles_swap(
        accion='comprar',
        modo_ingreso='total',  # El usuario ingresa la cantidad de fiat
        monto_form=Decimal('1000'),
        precio_origen_usdt=Decimal('1'),      # Precio de USDT
        precio_destino_usdt=Decimal('50000')  # Precio de BTC
    )
    
    assert exito is True
    assert detalles == {
        'origen': Decimal('1000'),    # Gastaré 1000 USDT
        'destino': Decimal('0.02'),   # Y recibiré 0.02 BTC
        'valor_usd': Decimal('1000')
    }

def test_venta_ingresando_monto_cripto():
    """
    Prueba una venta donde el usuario especifica la cantidad de cripto a VENDER.
    Ejemplo: Quiero vender exactamente 0.1 BTC.
    """
    exito, detalles = _calcular_detalles_swap(
        accion='vender',
        modo_ingreso='monto',  # En ventas, siempre se ingresa la cantidad de cripto
        monto_form=Decimal('0.1'),
        precio_origen_usdt=Decimal('50000'),  # Precio de BTC
        precio_destino_usdt=Decimal('1')      # Precio de USDT
    )
    
    assert exito is True
    assert detalles == {
        'origen': Decimal('0.1'),     # Venderé 0.1 BTC
        'destino': Decimal('5000'),   # Y recibiré 5000 USDT
        'valor_usd': Decimal('5000')
    }

# --- Tests para Casos Límite y Errores ---

def test_calculo_con_monto_cero():
    """
    Prueba que un monto de entrada cero resulte en un swap de valor cero.
    """
    exito, detalles = _calcular_detalles_swap(
        accion='comprar',
        modo_ingreso='total',
        monto_form=Decimal('0'),
        precio_origen_usdt=Decimal('1'),
        precio_destino_usdt=Decimal('50000')
    )
    
    assert exito is True
    assert detalles == {
        'origen': Decimal('0'),
        'destino': Decimal('0'),
        'valor_usd': Decimal('0')
    }

def test_calculo_con_precio_destino_cero():
    """
    Prueba que si el precio de destino es cero, no se puede recibir nada.
    """
    exito, detalles = _calcular_detalles_swap(
        accion='comprar',
        modo_ingreso='total',
        monto_form=Decimal('1000'),
        precio_origen_usdt=Decimal('1'),
        precio_destino_usdt=Decimal('0')  # Precio de destino es 0
    )
    
    assert exito is True
    # Si el precio de destino es 0, el valor total no puede convertirse en nada.
    # La implementación actual puede dar un ZeroDivisionError aquí, esto es un buen test para descubrirlo.
    # Asumiendo que se maneja, el destino debería ser 0.
    # NOTA: Este test podría fallar con ZeroDivisionError si no hay un try-except en la función.
    # Si la función no lo maneja, el test debería ser para esperar ese error.
    # Por ahora, asumimos que tu función es robusta. Si no, ¡este test te lo dirá!
    assert detalles['destino'] == Decimal('0')


def test_falla_al_vender_en_modo_total():
    """
    Prueba que la función falle si se intenta vender en modo 'total'.
    """
    exito, resultado = _calcular_detalles_swap(
        accion='vender',
        modo_ingreso='total',
        monto_form=Decimal('100'),
        precio_origen_usdt=Decimal('50000'),
        precio_destino_usdt=Decimal('1')
    )
    
    assert exito is False
    assert isinstance(resultado, str)
    assert "Al vender, debe ingresar la cantidad" in resultado

def test_falla_con_accion_desconocida():
    """
    Prueba que la función falle si la acción no es 'comprar' ni 'vender'.
    """
    exito, resultado = _calcular_detalles_swap(
        accion='intercambiar',
        modo_ingreso='monto',
        monto_form=Decimal('1'),
        precio_origen_usdt=Decimal('1'),
        precio_destino_usdt=Decimal('1')
    )
    
    assert exito is False
    assert "Acción de trading desconocida" in resultado