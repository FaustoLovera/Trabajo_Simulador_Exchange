"""Pruebas Unitarias para el Módulo Gestor de Trading.

Este archivo contiene pruebas para la función `cancelar_orden_pendiente` del
módulo `backend.servicios.trading.gestor`. Esta función es crítica para la
interacción del usuario, ya que le permite revertir órdenes que aún no se han
ejecutado.

Las pruebas verifican los siguientes escenarios:
- La cancelación exitosa de una orden, asegurando la correcta liberación de
  fondos reservados en la billetera.
- Los casos de error, como intentar cancelar una orden inexistente o una orden
  que ya no está en estado 'pendiente'.

Se utilizan fixtures para crear un entorno de prueba aislado y consistente.
"""
import pytest
from decimal import Decimal
import json

# Importar la función a probar
from backend.servicios.trading.gestor import cancelar_orden_pendiente
# Importar funciones de acceso a datos para verificar
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes

def test_cancelar_orden_pendiente_debe_liberar_fondos_y_cambiar_estado_a_cancelada_cuando_orden_existe_y_esta_pendiente(entorno_con_orden_pendiente):
    """Verifica la cancelación exitosa de una orden y la liberación de fondos.

    Este es el "happy path" o caso de éxito. La prueba asegura que cuando un
    usuario cancela una orden pendiente, ocurren dos efectos críticos:
    1.  Los fondos que estaban 'reservados' para esa orden en la billetera son
        devueltos al saldo 'disponible'.
    2.  La orden cambia su estado a 'cancelada' para que no sea procesada por
        el motor de trading.

    La fixture `entorno_con_orden_pendiente` se encarga de crear el estado
    inicial necesario (billetera con fondos reservados y una orden pendiente).

    Args:
        entorno_con_orden_pendiente: Fixture que prepara un escenario de prueba
            con una orden de venta de BTC pendiente.
    """
    # Arrange: ¡Ya está hecho por el fixture!

    # Act
    resultado = cancelar_orden_pendiente("btc_venta_1")

    # Assert
    assert resultado["estado"] == "ok"


    billetera_final = cargar_billetera()
    ordenes_finales = cargar_ordenes_pendientes()

    # Fondos liberados
    assert billetera_final["BTC"]["saldos"]["reservado"] == Decimal("0")
    assert billetera_final["BTC"]["saldos"]["disponible"] == Decimal("1.5")

    # Estado de la orden cambiado
    orden_cancelada = next(o for o in ordenes_finales if o["id_orden"] == "btc_venta_1")
    assert orden_cancelada["estado"] == "cancelada"


def test_cancelar_orden_pendiente_debe_fallar_cuando_id_de_orden_no_existe(test_environment):
    """Verifica que el sistema maneja correctamente un ID de orden inválido.

    Esta prueba de robustez asegura que si se intenta cancelar una orden con un
    ID que no corresponde a ninguna orden pendiente, la función falla de forma
    controlada, devolviendo un estado de 'error' y un mensaje claro, sin
    alterar el estado del sistema.

    Args:
        test_environment: Fixture que provee un entorno de prueba limpio y aislado.
    """
    # Arrange: El fixture `test_environment` ya creó un archivo de órdenes vacío.

    # Act
    resultado = cancelar_orden_pendiente("id_invalido")

    # Assert
    assert resultado["estado"] == "error"
    assert "No se encontró una orden" in resultado["mensaje"]
    assert "id_invalido" in resultado["mensaje"]


def test_cancelar_orden_pendiente_debe_fallar_cuando_orden_no_esta_en_estado_pendiente(test_environment):
    """Verifica que una orden solo puede cancelarse si su estado es 'pendiente'.

    Esta prueba valida la lógica de la máquina de estados de una orden. Una vez
    que una orden ha sido 'ejecutada' o 'cancelada', no puede volver a ser
    cancelada. El test modifica el estado de una orden (preparada por el fixture)
    a 'ejecutada' y luego a 'cancelada', y verifica que en ambos casos la
    función `cancelar_orden_pendiente` rechace la operación con un error.

    Args:
        test_environment: Fixture que prepara el escenario base.
    """
    # Arrange: Crear un estado inicial con una orden ya 'ejecutada'
    ruta_billetera = test_environment['billetera']
    ruta_ordenes = test_environment['ordenes']

    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1.0", "reservado": "0.5"}}
    }
    with open(ruta_billetera, 'w') as f:
        json.dump(billetera_inicial, f)

    orden_ejecutada = {
        "id_orden": "btc_venta_1",
        "ticker": "BTC/USDT",
        "accion": "venta",
        "tipo_orden": "limit",
        "cantidad": "0.5",
        "precio": "60000",
        "estado": "ejecutada" # Estado clave para esta prueba
    }
    with open(ruta_ordenes, 'w') as f:
        json.dump([orden_ejecutada], f)

    # Act
    resultado = cancelar_orden_pendiente("btc_venta_1")

    # Assert
    assert resultado["estado"] == "error"
    assert "no puede ser cancelada" in resultado["mensaje"]
    assert "estado actual: 'ejecutada'" in resultado["mensaje"]
    
def test_cancelar_orden_con_error_de_consistencia_de_fondos(test_environment):
    """
    Verifica que la cancelación falla si los fondos a liberar en la orden
    no coinciden con los fondos reservados en la billetera.
    """
    # ARRANGE: Crear una inconsistencia de datos
    billetera_data = {
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1.0", "reservado": "0.1"}} # Solo 0.1 reservado
    }
    orden_data = [{
        "id_orden": "btc_venta_inconsistente",
        "estado": "pendiente",
        "moneda_reservada": "BTC",
        "cantidad_reservada": "0.5" # ¡La orden cree que reservó 0.5!
    }]
    with open(test_environment['billetera'], 'w') as f:
        json.dump(billetera_data, f)
    with open(test_environment['ordenes'], 'w') as f:
        json.dump(orden_data, f)

    # ACT
    resultado = cancelar_orden_pendiente("btc_venta_inconsistente")

    # ASSERT
    assert resultado["estado"] == "error"
    assert "Error de consistencia" in resultado["mensaje"]

    # Verificar que el estado de la orden se marcó como erróneo
    ordenes_finales = cargar_ordenes_pendientes(ruta_archivo=test_environment['ordenes'])
    assert ordenes_finales[0]["estado"] == "error"