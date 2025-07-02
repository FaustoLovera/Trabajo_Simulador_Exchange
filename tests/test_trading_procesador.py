"""Pruebas Unitarias para el Procesador de Operaciones de Trading.

Este archivo contiene pruebas para el módulo `procesador_operacion_trading`,
que es el servicio de más alto nivel que orquesta una operación de trading
iniciada por el usuario. Su responsabilidad abarca desde la validación inicial
de los datos hasta la ejecución directa (órdenes de mercado) o la creación
de órdenes pendientes (Limit, Stop-Limit).

Las pruebas cubren:
- Funciones de validación puras (ej. `_validar_saldo_disponible`).
- La creación de órdenes pendientes y sus efectos secundarios (reserva de fondos).
- La validación de la entrada del usuario en la función principal.
"""

import pytest
from decimal import Decimal
import json

from backend.servicios.trading.procesador import _validar_saldo_disponible, _calcular_detalles_intercambio
from backend.servicios.trading.procesador import _crear_orden_pendiente, procesar_operacion_trading
from config import BILLETERA_PATH, ORDENES_PENDIENTES_PATH

def test_validar_saldo_disponible_debe_retornar_exito_cuando_saldo_es_suficiente():
    """Verifica que la validación es exitosa si hay saldo disponible."""
    billetera_fake = {"BTC": {"saldos": {"disponible": Decimal("2.5")}}}
    exito, mensaje = _validar_saldo_disponible(billetera_fake, "BTC", Decimal("1.0"))
    assert exito is True

def test_validar_saldo_disponible_debe_fallar_cuando_saldo_es_insuficiente():
    """Verifica que la validación falla si el saldo es insuficiente."""
    billetera_fake = {"BTC": {"saldos": {"disponible": Decimal("2.5")}}}
    exito, mensaje = _validar_saldo_disponible(billetera_fake, "BTC", Decimal("3.0"))
    assert exito is False
    assert "Saldo insuficiente" in mensaje

def test_crear_orden_pendiente_debe_preparar_orden_y_billetera_en_memoria(mocker):
    """
    Verifica que _crear_orden_pendiente (ahora una función pura) devuelve
    correctamente la nueva orden y la billetera modificada en memoria, sin
    realizar I/O.
    """
    # ARRANGE
    # 1. Mock de la dependencia externa (obtener_precio) para aislar la prueba.
    mocker.patch('backend.servicios.trading.procesador.obtener_precio', return_value=Decimal('1.0'))

    # 2. Crear una billetera inicial en memoria.
    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": Decimal("10000"), "reservado": Decimal("0")}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": Decimal("1"), "reservado": Decimal("0")}}
    }

    # ACT
    exito, resultado = _crear_orden_pendiente(
        billetera=billetera_inicial,
        moneda_origen='USDT',
        moneda_destino='BTC',
        monto_form=Decimal('1000'),
        modo_ingreso='total',
        precio_disparo=Decimal('40000'),
        tipo_orden='limit',
        accion='compra',
        precio_limite=None
    )

    # ASSERT
    assert exito is True
    
    # 1. Verificar la orden creada (devuelta en el resultado)
    orden_creada = resultado['orden']
    assert orden_creada['estado'] == 'pendiente'
    assert orden_creada['accion'] == 'compra'
    assert orden_creada['par'] == 'BTC/USDT'
    assert orden_creada['moneda_reservada'] == 'USDT'
    # En modo 'total', la cantidad a reservar es el monto del formulario.
    assert Decimal(orden_creada['cantidad_reservada']) == Decimal('1000')

    # 2. Verificar la billetera modificada (devuelta en el resultado)
    billetera_final = resultado['billetera']
    assert billetera_final['USDT']['saldos']['disponible'] == Decimal('9000')
    assert billetera_final['USDT']['saldos']['reservado'] == Decimal('1000')

def test_procesar_operacion_trading_debe_fallar_cuando_monto_es_negativo_o_cero(test_environment):
    """Verifica que la función principal rechaza montos negativos o inválidos."""
    formulario_malo = {"ticker": "BTC", "accion": "compra", "monto": "-100"}
    respuesta = procesar_operacion_trading(formulario_malo)
    assert respuesta["estado"] == "error"
    assert "monto debe ser un número positivo" in respuesta["mensaje"]


def test_procesar_operacion_trading_debe_fallar_cuando_monedas_son_identicas(test_environment):
    """Verifica que la operación falla si la moneda de origen y destino son la misma."""
    # Para una compra, moneda-pago (origen) y ticker (destino) son iguales
    formulario_compra_malo = {
        "ticker": "USDT", 
        "accion": "compra", 
        "monto": "100",
        "moneda-pago": "USDT"
    }
    respuesta_compra = procesar_operacion_trading(formulario_compra_malo)
    assert respuesta_compra["estado"] == "error"
    assert "La moneda de origen y destino no pueden ser la misma" in respuesta_compra["mensaje"]

    # Para una venta, ticker (origen) y moneda-recibir (destino) son iguales
    formulario_venta_malo = {
        "ticker": "BTC", 
        "accion": "venta", 
        "monto": "1",
        "moneda-recibir": "BTC"
    }
    respuesta_venta = procesar_operacion_trading(formulario_venta_malo)
    assert respuesta_venta["estado"] == "error"
    assert "La moneda de origen y destino no pueden ser la misma" in respuesta_venta["mensaje"]


def test_procesar_operacion_trading_debe_fallar_cuando_tipo_orden_es_invalido(test_environment):
    """Verifica que la operación falla si se provee un tipo de orden no soportado."""
    formulario_malo = {
        "ticker": "BTC", 
        "accion": "compra", 
        "monto": "100",
        "tipo-orden": "tipo_invalido"
    }
    respuesta = procesar_operacion_trading(formulario_malo)
    assert respuesta["estado"] == "error"
    assert "Tipo de orden 'tipo_invalido' no soportado" in respuesta["mensaje"]


def test_crear_orden_pendiente_debe_fallar_si_saldo_es_insuficiente(mocker):
    """
    Verifica que _crear_orden_pendiente (función pura) falla y devuelve un
    error claro cuando no hay suficientes fondos, sin realizar I/O.
    """
    # ARRANGE
    mocker.patch('backend.servicios.trading.procesador.obtener_precio', return_value=Decimal('1.0'))
    
    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": Decimal("500"), "reservado": Decimal("0")}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": Decimal("1"), "reservado": Decimal("0")}}
    }

    # ACT
    exito, resultado = _crear_orden_pendiente(
        billetera=billetera_inicial,
        moneda_origen='USDT',
        moneda_destino='BTC',
        monto_form=Decimal('1000'), # Intentar gastar 1000 USDT
        modo_ingreso='total',
        precio_disparo=Decimal('40000'),
        tipo_orden='limit',
        accion='compra',
        precio_limite=None
    )

    # ASSERT
    assert exito is False
    assert "error" in resultado
    assert "Saldo insuficiente" in resultado["error"]