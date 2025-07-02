"""Pruebas Unitarias para el Módulo de Ejecución de Transacciones.

Este archivo se enfoca en probar la función `ejecutar_transaccion`, que es el
corazón de la lógica de trading de más bajo nivel. Esta función es responsable
de la operación atómica que modifica los saldos de la billetera y crea los
registros de historial y comisiones correspondientes.

Las pruebas aquí verifican:
- El cálculo correcto de las cantidades (neta, destino, comisión).
- La actualización precisa de los saldos de la billetera (disponible/reservado).
- La correcta creación y persistencia de los registros en los archivos de
  historial y comisiones.
- La consistencia de los datos devueltos por la función.
"""

import pytest
import json
from decimal import Decimal

from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from config import TASA_COMISION

def test_ejecutar_transaccion_debe_completar_compra_y_actualizar_archivos_cuando_es_orden_de_mercado_valida(test_environment):
    """Verifica el flujo completo y exitoso de una orden de compra a mercado."""
    # ARRANGE: Poblar los archivos temporales creados por el fixture
    ruta_billetera = test_environment['billetera']
    ruta_cotizaciones = test_environment['cotizaciones']
    ruta_historial = test_environment['historial']
    ruta_comisiones = test_environment['comisiones']

    # 1. Poblar billetera.json inicial
    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1.0", "reservado": "0.5"}}
    }
    with open(ruta_billetera, 'w') as f:
        json.dump(billetera_inicial, f)

    # 2. Poblar cotizaciones.json con precios
    cotizaciones = [
        {"ticker": "USDT", "precio_usd": "1.0"},
        {"ticker": "BTC", "precio_usd": "50000.0"}
    ]
    with open(ruta_cotizaciones, 'w') as f:
        json.dump(cotizaciones, f)
        
    # ACT: Ejecutar la transacción
    cantidad_a_gastar_bruta = Decimal('1000')
    billetera_cargada = cargar_billetera(ruta_billetera)

    exito, detalles = ejecutar_transaccion(
        billetera=billetera_cargada,
        moneda_origen='USDT',
        cantidad_origen_bruta=cantidad_a_gastar_bruta,
        moneda_destino='BTC',
        tipo_operacion_historial='Compra Mercado',
        es_orden_pendiente=False,
        ruta_cotizaciones=ruta_cotizaciones
    )
    # Persistir los cambios en la billetera para que la aserción los pueda leer del archivo
    guardar_billetera(billetera_cargada, ruta_archivo=ruta_billetera)

    # ASSERT: Verificar el estado final
    assert exito is True

    # 1. Verificar detalles devueltos
    comision_esperada = cantidad_a_gastar_bruta * TASA_COMISION
    cantidad_neta_esperada = cantidad_a_gastar_bruta - comision_esperada
    cantidad_destino_esperada = cantidad_neta_esperada / Decimal('50000')
    assert detalles['cantidad_comision'] == comision_esperada
    assert detalles['cantidad_destino_final'] == cantidad_destino_esperada

    # 2. Verificar historial.json
    with open(ruta_historial, 'r') as f:
        historial = json.load(f)
    assert len(historial) == 1
    assert historial[0]['tipo'] == 'Compra Mercado'
    assert historial[0]['destino']['ticker'] == 'BTC'

    # 3. Verificar comisiones.json
    with open(ruta_comisiones, 'r') as f:
        comisiones = json.load(f)
    assert len(comisiones) == 1
    assert comisiones[0]['ticker'] == 'USDT'
    assert Decimal(comisiones[0]['cantidad']) == comision_esperada.quantize(Decimal("0.00000001"))

    # 4. Verificar billetera.json
    with open(ruta_billetera, 'r') as f:
        billetera_final = json.load(f)
    saldo_usdt_final = Decimal(billetera_final['USDT']['saldos']['disponible'])
    saldo_btc_final = Decimal(billetera_final['BTC']['saldos']['disponible'])
    assert saldo_usdt_final == Decimal('9000')
    assert saldo_btc_final == Decimal('1.0') + cantidad_destino_esperada

    # 4. Verificar el estado final de la billetera (leyendo el objeto modificado)
    assert billetera_cargada['USDT']['saldos']['disponible'] == Decimal('9000') # 10000 - 1000
    assert billetera_cargada['BTC']['saldos']['disponible'] == Decimal('1') + cantidad_destino_esperada
    assert billetera_cargada['BTC']['saldos']['reservado'] == Decimal('0.5') # No debe cambiar