# --- FILENAME: tests/test_ejecutar_orden.py ---

import pytest
import json
from decimal import Decimal

from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.acceso_datos.datos_billetera import cargar_billetera
from config import TASA_COMISION, BILLETERA_PATH, COTIZACIONES_PATH, HISTORIAL_PATH, COMISIONES_PATH

def test_ejecucion_exitosa_orden_mercado(test_environment):
    """
    Prueba un flujo de compra de mercado completo, verificando los archivos resultantes.
    """
    # ARRANGE: Crear los archivos necesarios en el directorio temporal
    # 1. Crear billetera.json inicial
    billetera_inicial_dict = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1.0", "reservado": "0.5"}}
    }
    with open(BILLETERA_PATH, 'w') as f:
        json.dump(billetera_inicial_dict, f)

    # 2. Crear cotizaciones.json con precios
    cotizaciones_dict = [
        {"ticker": "USDT", "precio_usd": "1.0"},
        {"ticker": "BTC", "precio_usd": "50000.0"}
    ]
    with open(COTIZACIONES_PATH, 'w') as f:
        json.dump(cotizaciones_dict, f)
        
    # ACT: Ejecutar la transacción
    cantidad_a_gastar_bruta = Decimal('1000')
    billetera_cargada = cargar_billetera() # La función a probar necesita el objeto billetera

    exito, detalles = ejecutar_transaccion(
        billetera=billetera_cargada,
        moneda_origen='USDT',
        cantidad_origen_bruta=cantidad_a_gastar_bruta,
        moneda_destino='BTC',
        tipo_operacion_historial='Compra Mercado',
        es_orden_pendiente=False
    )

    # ASSERT: Verificar el estado final de los archivos
    assert exito is True

    # 1. Verificar el diccionario de detalles devuelto
    comision_esperada = cantidad_a_gastar_bruta * TASA_COMISION
    cantidad_neta_esperada = cantidad_a_gastar_bruta - comision_esperada
    cantidad_destino_esperada = cantidad_neta_esperada / Decimal('50000')
    assert detalles['cantidad_comision'] == comision_esperada
    assert detalles['cantidad_destino_final'] == cantidad_destino_esperada

    # 2. Verificar el archivo de historial
    with open(HISTORIAL_PATH, 'r') as f:
        historial = json.load(f)
    assert len(historial) == 1
    assert historial[0]['tipo'] == 'Compra Mercado'
    assert historial[0]['destino']['ticker'] == 'BTC'

    # 3. Verificar el archivo de comisiones
    with open(COMISIONES_PATH, 'r') as f:
        comisiones = json.load(f)
    assert len(comisiones) == 1
    assert comisiones[0]['ticker'] == 'USDT'
    assert Decimal(comisiones[0]['cantidad']) == comision_esperada.quantize(Decimal("0.00000001"))

    # 4. Verificar el estado final de la billetera (leyendo el objeto modificado)
    assert billetera_cargada['USDT']['saldos']['disponible'] == Decimal('9000') # 10000 - 1000
    assert billetera_cargada['BTC']['saldos']['disponible'] == Decimal('1') + cantidad_destino_esperada
    assert billetera_cargada['BTC']['saldos']['reservado'] == Decimal('0.5') # No debe cambiar