"""Pruebas de Integración y Unitarias para el Procesador de Trading.

Este archivo se centra en probar `procesar_operacion_trading`, el punto de
entrada principal para las operaciones. Dado que la lógica de creación de
órdenes ahora está integrada, las pruebas se enfocan en verificar el
comportamiento de alto nivel y sus efectos secundarios, como la modificación
de archivos de estado (billetera, órdenes pendientes).

Las pruebas cubren:
- Flujos de error principales (datos de formulario inválidos).
- Flujo completo de creación de una orden límite, incluyendo:
  - La correcta reserva de fondos en la billetera.
  - La creación de la orden en el archivo de órdenes pendientes.
- Casos de fallo, como la falta de fondos, y la no alteración de los archivos.
"""

import pytest
from decimal import Decimal
import json

from backend.servicios.trading.procesador import _validar_saldo_disponible, procesar_operacion_trading
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

def test_procesar_operacion_trading_debe_fallar_cuando_monto_es_negativo_o_cero(test_environment):
    """Verifica que la función principal rechaza montos negativos o inválidos."""
    formulario_malo = {"ticker": "BTC", "accion": "compra", "monto": "-100"}
    respuesta = procesar_operacion_trading(formulario_malo)
    assert respuesta["estado"] == "error"
    assert "monto debe ser un número positivo" in respuesta["mensaje"]

def test_procesar_operacion_trading_debe_fallar_cuando_monedas_son_identicas(test_environment):
    """Verifica que la operación falla si la moneda de origen y destino son la misma."""
    # Para una compra de USDT, la moneda de origen (por defecto) y destino son la misma.
    formulario_compra_malo = {
        "ticker": "USDT", 
        "accion": "compra", 
        "monto": "100",
    }
    respuesta_compra = procesar_operacion_trading(formulario_compra_malo)
    assert respuesta_compra["estado"] == "error"
    assert "La moneda de origen y destino no pueden ser la misma" in respuesta_compra["mensaje"]

# --- Nuevos Tests de Integración para Órdenes Límite ---

def test_procesar_operacion_limit_exitosa_reserva_fondos_y_crea_orden(test_environment):
    """
    Test de integración: Verifica que una orden LÍMITE de compra válida:
    1. Devuelve una respuesta exitosa.
    2. Reserva los fondos correctamente en la billetera.
    3. Crea una nueva orden en el archivo de órdenes pendientes.
    """
    # ARRANGE
    # 1. Escribir una billetera inicial con fondos suficientes.
    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000", "reservado": "0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1", "reservado": "0"}}
    }
    with open(test_environment['billetera'], 'w') as f:
        json.dump(billetera_inicial, f, indent=4)

    # 2. Formulario para una orden de compra límite
    formulario = {
        "ticker": "BTC",
        "accion": "compra",
        "monto": "500",  # Comprar con 500 USDT
        "modo-ingreso": "total",
        "tipo-orden": "limit",
        "precio_disparo": "20000" # Precio límite
    }

    # ACT
    respuesta = procesar_operacion_trading(formulario)

    # ASSERT
    # 1. La respuesta debe ser exitosa.
    assert respuesta["estado"] == "ok"
    assert "Orden Límite creada" in respuesta["mensaje"]

    # 2. Verificar el estado final de la billetera.
    with open(test_environment['billetera'], 'r') as f:
        billetera_final = json.load(f)
    
    assert Decimal(billetera_final["USDT"]["saldos"]["disponible"]) == Decimal("9500")
    assert Decimal(billetera_final["USDT"]["saldos"]["reservado"]) == Decimal("500")

    # 3. Verificar que la orden fue creada en el archivo de pendientes.
    cotizaciones = [{"ticker": "BTC", "precio_usd": "25000"}]
    with open(test_environment['cotizaciones'], 'w') as f:
        json.dump(cotizaciones, f)
    
    assert len(ordenes_pendientes) == 1
    orden_creada = ordenes_pendientes[0]
    assert orden_creada["par"] == "BTC/USDT"
    assert orden_creada["accion"] == "compra"
    assert orden_creada["tipo"] == "limit"
    assert Decimal(orden_creada["precio_limite"]) == Decimal("20000")
    # Cantidad de BTC a comprar: 500 USDT / 20000 USD/BTC = 0.025 BTC
    assert Decimal(orden_creada["cantidad"]) == Decimal("0.025")

def test_procesar_operacion_limit_falla_por_fondos_insuficientes(test_environment):
    """
    Test de integración: Verifica que una orden LÍMITE falla si no hay
    fondos suficientes y que el estado de los archivos no cambia.
    """
    # ARRANGE
    # 1. Billetera con fondos insuficientes.
    billetera_inicial = {
    "USDT": {"nombre": "Tether", "saldos": {"disponible": "100", "reservado": "0"}},
    }
    with open(test_environment['billetera'], 'w') as f:
        json.dump(billetera_inicial, f, indent=4)
    
    # 2. Formulario que intenta gastar más de lo disponible.
    formulario = {
        "ticker": "BTC",
        "accion": "compra",
        "monto": "500",  # Intentar gastar 500 USDT
        "modo-ingreso": "total",
        "tipo-orden": "limit",
        "precio_disparo": "20000"
    }

    # ACT
    respuesta = procesar_operacion_trading(formulario)

    # ASSERT
    # 1. La respuesta debe ser de error.
    assert respuesta["estado"] == "error"
    assert "Saldo insuficiente" in respuesta["mensaje"]

    # 2. Verificar que las órdenes pendientes siguen vacías.
    with open(test_environment['ordenes'], 'r') as f:
        ordenes_pendientes = json.load(f)
    assert len(ordenes_pendientes) == 0

    # 3. Verificar que la billetera no fue modificada.
    with open(test_environment['billetera'], 'r') as f:
        billetera_final = json.load(f)
    assert billetera_final == billetera_inicial
    
    
@pytest.mark.parametrize("formulario, mensaje_error_esperado", [
    # Compra Stop-Limit: El precio Stop debe ser MAYOR al de mercado
    ({
        "ticker": "BTC", "accion": "compra", "monto": "0.1", "modo-ingreso": "monto",
        "tipo-orden": "stop-limit", "precio_disparo": "49000", "precio_limite": "50000"
    }, "debe ser > al precio actual"),
    # Venta Stop-Limit: El precio Stop debe ser MENOR al de mercado
    ({
        "ticker": "BTC", "accion": "venta", "monto": "0.1", "modo-ingreso": "monto",
        "tipo-orden": "stop-limit", "precio_disparo": "51000", "precio_limite": "50000"
    }, "debe ser < al precio actual"),
    # Compra Stop-Limit: El precio Límite no puede ser MENOR al Stop
    ({
        "ticker": "BTC", "accion": "compra", "monto": "0.1", "modo-ingreso": "monto",
        "tipo-orden": "stop-limit", "precio_disparo": "51000", "precio_limite": "50000"
    }, "no puede ser < al Precio Stop"),
    # Venta Stop-Limit: El precio Límite no puede ser MAYOR al Stop
    ({
        "ticker": "BTC", "accion": "venta", "monto": "0.1", "modo-ingreso": "monto",
        "tipo-orden": "stop-limit", "precio_disparo": "49000", "precio_limite": "50000"
    }, "no puede ser > al Precio Stop"),
])
def test_procesar_operacion_stop_limit_falla_por_reglas_de_precio_invalidas(test_environment, formulario, mensaje_error_esperado):
    """Verifica las reglas de validación de precios para órdenes Stop-Limit."""
    # ARRANGE: Establecer un precio de mercado de referencia
    cotizaciones = [{"ticker": "BTC", "precio_usd": "50000"}]
    with open(test_environment['cotizaciones'], 'w') as f:
        json.dump(cotizaciones, f)
    
    # ACT
    respuesta = procesar_operacion_trading(formulario)

    # ASSERT
    assert respuesta["estado"] == "error"
    assert mensaje_error_esperado in respuesta["mensaje"]