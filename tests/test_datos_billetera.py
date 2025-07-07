"""
Pruebas Unitarias para el Módulo de Acceso a Datos de la Billetera.

Este archivo se enfoca en verificar la robustez y correcta funcionalidad del
módulo `datos_billetera.py`, especialmente en su interacción con el sistema
de archivos.
"""

import os
import json
import pytest
from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera, _crear_billetera_inicial
import config

def test_cargar_billetera_crea_una_nueva_si_no_existe(test_environment):
    """
    Verifica que `cargar_billetera` crea una billetera inicial si el archivo
    JSON no se encuentra.
    """
    # ARRANGE: El fixture test_environment ya nos da una ruta limpia.
    # Nos aseguramos de que el archivo no exista.
    ruta_billetera = test_environment['billetera']
    if_exists_delete(ruta_billetera)

    # ACT
    billetera_cargada = cargar_billetera(ruta_archivo=ruta_billetera)

    # ASSERT
    billetera_inicial_esperada = _crear_billetera_inicial()
    assert billetera_cargada == billetera_inicial_esperada
    assert billetera_cargada["USDT"]["saldos"]["disponible"] == Decimal(config.BALANCE_INICIAL_USDT)

    # Verificar que el archivo fue creado
    try:
        with open(ruta_billetera, 'r') as f:
            datos_en_archivo = json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")

    # --- FIX APLICADO AQUÍ ---
    # Convertir ambos valores a Decimal antes de la comparación para ignorar
    # diferencias de formato como los ceros decimales.
    saldo_en_archivo = Decimal(datos_en_archivo["USDT"]["saldos"]["disponible"])
    saldo_esperado = Decimal(config.BALANCE_INICIAL_USDT)
    assert saldo_en_archivo == saldo_esperado

def test_cargar_billetera_reinicia_si_el_archivo_esta_corrupto(test_environment):
    """
    Verifica que `cargar_billetera` reinicia a una billetera inicial si el
    archivo JSON está mal formado.
    """
    # ARRANGE: Escribir un JSON inválido en el archivo de billetera.
    ruta_billetera = test_environment['billetera']
    try:
        with open(ruta_billetera, 'w') as f:
            f.write("{'json_invalido': 'con comillas simples'}")
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")

    # ACT
    billetera_cargada = cargar_billetera(ruta_archivo=ruta_billetera)

    # ASSERT
    billetera_inicial_esperada = _crear_billetera_inicial()
    assert billetera_cargada == billetera_inicial_esperada
    assert billetera_cargada["USDT"]["saldos"]["disponible"] == Decimal(config.BALANCE_INICIAL_USDT)

def test_guardar_y_cargar_billetera_ciclo_completo(test_environment):
    """
    Verifica que los datos guardados con `guardar_billetera` son correctamente
    leídos por `cargar_billetera`.
    """
    # ARRANGE: Crear un estado de billetera complejo.
    ruta_billetera = test_environment['billetera']
    billetera_a_guardar = {
        "USDT": {"saldos": {"disponible": Decimal("1234.5678"), "reservado": Decimal("500")}},
        "BTC": {"saldos": {"disponible": Decimal("1.23456789"), "reservado": Decimal("0.5")}}
    }

    # ACT
    guardar_billetera(billetera_a_guardar, ruta_archivo=ruta_billetera)
    billetera_cargada = cargar_billetera(ruta_archivo=ruta_billetera)

    # ASSERT
    # Comprobar que los valores Decimal se han conservado después del ciclo de guardado/cargado.
    assert billetera_cargada["USDT"]["saldos"]["disponible"] == Decimal("1234.5678")
    assert billetera_cargada["USDT"]["saldos"]["reservado"] == Decimal("500.0000") # La cuantización añade ceros
    assert billetera_cargada["BTC"]["saldos"]["disponible"] == Decimal("1.23456789")
    assert billetera_cargada["BTC"]["saldos"]["reservado"] == Decimal("0.50000000")

# --- Función de ayuda para los tests ---

def if_exists_delete(filepath):
    """Función de utilidad para eliminar un archivo si existe."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")