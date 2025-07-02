# --- FILENAME: tests/test_trading_procesador.py ---

import pytest
from decimal import Decimal
import json

# Las funciones de bajo nivel son "puras", sus tests no necesitan mocks
from backend.servicios.trading.procesador import _validar_saldo_disponible, _calcular_detalles_intercambio
# Probaremos esta función que sí interactúa con archivos
from backend.servicios.trading.procesador import _crear_orden_pendiente
from config import BILLETERA_PATH, ORDENES_PENDIENTES_PATH

# --- Tests para funciones puras (sin cambios) ---

def test_validar_saldo_suficiente():
    billetera_fake = {"BTC": {"saldos": {"disponible": Decimal("2.5")}}}
    exito, mensaje = _validar_saldo_disponible(billetera_fake, "BTC", Decimal("1.0"))
    assert exito is True

def test_validar_saldo_insuficiente():
    billetera_fake = {"BTC": {"saldos": {"disponible": Decimal("2.5")}}}
    exito, mensaje = _validar_saldo_disponible(billetera_fake, "BTC", Decimal("3.0"))
    assert exito is False
    assert "Saldo insuficiente" in mensaje

# ... (puedes mantener el test parametrizado de _calcular_detalles_intercambio si quieres) ...

# --- Test para _crear_orden_pendiente (estilo básico) ---

def test_crear_orden_limite_reserva_fondos_correctamente(test_environment):
    """
    Prueba que se crea una orden pendiente y se reservan los fondos en la billetera.
    """
    # ARRANGE: Crear el archivo de billetera inicial
    billetera_inicial_dict = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "2.5", "reservado": "0.0"}}
    }
    with open(BILLETERA_PATH, 'w') as f:
        json.dump(billetera_inicial_dict, f)

    # ACT: Llamar a la función para crear una orden de compra límite gastando 1000 USDT
    exito, resultado = _crear_orden_pendiente(
        moneda_origen='USDT', 
        moneda_destino='BTC', 
        monto_form=Decimal('1000'), 
        modo_ingreso='total', 
        precio_disparo=Decimal('40000'), 
        tipo_orden='limit', 
        accion='comprar',
        precio_limite=None
    )

    # ASSERT
    assert exito is True
    assert "Orden Limit Creada" in resultado["titulo"]

    # 1. Verificar el archivo de órdenes pendientes
    with open(ORDENES_PENDIENTES_PATH, 'r') as f:
        ordenes = json.load(f)
    assert len(ordenes) == 1
    orden_creada = ordenes[0]
    assert orden_creada['estado'] == 'pendiente'
    assert orden_creada['accion'] == 'comprar'
    assert orden_creada['par'] == 'BTC/USDT' # Corregido: El par debe ser MonedaPrincipal/MonedaCotizada (BTC/USDT)
    assert orden_creada['moneda_reservada'] == 'USDT'
    assert Decimal(orden_creada['cantidad_reservada']) == Decimal('1000')

    # 2. Verificar el archivo de billetera modificado
    with open(BILLETERA_PATH, 'r') as f:
        billetera_final = json.load(f)
    assert Decimal(billetera_final['USDT']['saldos']['disponible']) == Decimal('9000')
    assert Decimal(billetera_final['USDT']['saldos']['reservado']) == Decimal('1000')