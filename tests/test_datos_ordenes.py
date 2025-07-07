"""
Pruebas Unitarias para el Módulo de Acceso a Datos de Órdenes.
"""

import json
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes

def test_cargar_ordenes_pendientes_devuelve_lista_vacia_si_archivo_corrupto(test_environment):
    """
    Verifica que `cargar_ordenes_pendientes` devuelve una lista vacía si el archivo
    JSON está mal formado, en lugar de lanzar una excepción.
    """
    # ARRANGE: Escribir datos inválidos en el archivo de órdenes.
    ruta_ordenes = test_environment['ordenes']
    try:
        with open(ruta_ordenes, 'w') as f:
            f.write("esto no es un json")
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")

    # ACT
    ordenes = cargar_ordenes_pendientes(ruta_archivo=ruta_ordenes)

    # ASSERT
    assert ordenes == []

def test_guardar_ordenes_pendientes_sobrescribe_correctamente(test_environment):
    """
    Verifica que guardar una nueva lista de órdenes sobrescribe la anterior.
    """
    # ARRANGE
    ruta_ordenes = test_environment['ordenes']
    ordenes_iniciales = [{"id_orden": "1", "estado": "pendiente"}]
    ordenes_nuevas = [{"id_orden": "2", "estado": "pendiente"}, {"id_orden": "3", "estado": "cancelada"}]
    
    guardar_ordenes_pendientes(ordenes_iniciales, ruta_archivo=ruta_ordenes)

    # ACT
    guardar_ordenes_pendientes(ordenes_nuevas, ruta_archivo=ruta_ordenes)
    
    # ASSERT
    ordenes_cargadas = cargar_ordenes_pendientes(ruta_archivo=ruta_ordenes)
    assert len(ordenes_cargadas) == 2
    assert ordenes_cargadas[0]['id_orden'] == '2'
    assert ordenes_cargadas == ordenes_nuevas