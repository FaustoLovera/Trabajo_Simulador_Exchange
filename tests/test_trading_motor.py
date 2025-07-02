"""Pruebas Unitarias para el Motor de Trading.

Este archivo prueba el motor de trading (`backend.servicios.trading.motor`), que
es el componente responsable de verificar y ejecutar automáticamente las órdenes
pendientes (Limit, Stop-Limit) cuando las condiciones del mercado son favorables.

Las pruebas se dividen en dos partes:
1.  **Prueba de Lógica Pura**: Se utiliza una prueba parametrizada para validar
    la función `_verificar_condicion_orden`, que contiene las reglas de negocio
    esenciales para decidir si una orden debe dispararse.
2.  **Prueba de Integración**: Se prueba la función principal
    `verificar_y_ejecutar_ordenes_pendientes`, asegurando que el motor lee
    correctamente los datos de mercado, identifica órdenes ejecutables y
    orquesta la transacción, modificando los archivos de estado (órdenes,
    billetera, historial).
"""
import pytest
import json
from decimal import Decimal

# Funciones puras a probar
from backend.servicios.trading.motor import _verificar_condicion_orden
# Función principal de integración a probar
from backend.servicios.trading.motor import verificar_y_ejecutar_ordenes_pendientes

# Funciones de acceso a datos para verificar resultados
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes

# Módulo de configuración para redirigir rutas
import config

# --- Tests para la lógica pura de verificación (sin cambios) ---

@pytest.mark.parametrize("accion, tipo, precio_limite, precio_mercado, esperado", [
    ("compra", "limit", "40000", "39000", True),
    ("compra", "limit", "40000", "40001", False),
    ("venta", "limit", "60000", "61000", True),
    ("venta", "limit", "60000", "59999", False),
    ("compra", "stop-limit", "55000", "56000", True),
    ("compra", "stop-limit", "55000", "54999", False),
    ("venta", "stop-limit", "45000", "44000", True),
    ("venta", "stop-limit", "45000", "45001", False),
])
def test_verificar_condicion_orden_debe_evaluar_correctamente_condiciones_de_disparo_para_todos_los_tipos_de_orden(accion, tipo, precio_limite, precio_mercado, esperado):
    """Valida de forma exhaustiva las reglas de negocio para disparar órdenes.

    Esta prueba parametrizada es fundamental, ya que verifica el corazón lógico
    del motor de trading. Cubre todos los casos posibles para los tipos de
    órdenes soportados:

    -   **Compra Limit**: Se ejecuta si `precio_mercado <= precio_limite`.
    -   **Venta Limit**: Se ejecuta si `precio_mercado >= precio_limite`.
    -   **Compra Stop-Limit**: Se ejecuta si `precio_mercado >= precio_disparo`.
    -   **Venta Stop-Limit**: Se ejecuta si `precio_mercado <= precio_disparo`.

    El uso de `@pytest.mark.parametrize` hace que el test sea conciso, legible
    y fácil de extender con nuevos casos.

    Args:
        accion (str): 'compra' o 'venta'.
        tipo (str): 'limit' o 'stop-limit'.
        precio_limite (str): El precio límite o de disparo de la orden.
        precio_mercado (str): El precio actual del mercado a verificar.
        esperado (bool): El resultado esperado de la verificación.
    """
    orden = {"accion": accion, "tipo_orden": tipo, "precio_disparo": precio_limite}
    assert _verificar_condicion_orden(orden, Decimal(precio_mercado)) is esperado

# --- Tests para la función principal del motor (simplificados) ---

def crear_archivo_json(ruta, contenido):
    """Crea un archivo JSON en la ruta especificada con el contenido dado.

    Args:
        ruta (str): La ruta completa del archivo a crear.
        contenido (dict or list): El objeto de Python a serializar en JSON.
    """
    with open(ruta, 'w') as f:
        json.dump(contenido, f, indent=4)

def test_verificar_y_ejecutar_ordenes_pendientes_debe_ejecutar_orden_cuando_condicion_de_mercado_es_favorable(tmp_path):
    """Prueba de integración del motor de trading en un escenario de ejecución.

    Este test verifica el flujo completo del motor en un caso de éxito:
    una orden de compra límite cuyo precio de mercado es favorable.

    Flujo de la prueba:
    1.  **Arrange**: Se configura un entorno de archivos temporales (billetera,
        órdenes, cotizaciones, etc.) usando `tmp_path`. Se crea una orden de
        compra límite y se establece un precio de mercado que cumple la condición.
    2.  **Act**: Se invoca a `verificar_y_ejecutar_ordenes_pendientes()`.
    3.  **Assert**: Se verifica que la ejecución tuvo los efectos esperados:
        - El estado de la orden en `ordenes.json` cambia a 'ejecutada'.
        - Los fondos reservados en `billetera.json` se utilizan.
        - El nuevo activo (BTC) se añade a la billetera.

    Args:
        tmp_path: Fixture de pytest que proporciona un directorio temporal.
    """
    # Arrange: Preparar el entorno de archivos temporales
    datos_dir = tmp_path / "datos"
    datos_dir.mkdir()
    config.BILLETERA_PATH = str(datos_dir / "billetera.json")
    config.ORDENES_PENDIENTES_PATH = str(datos_dir / "ordenes.json")
    config.COTIZACIONES_PATH = str(datos_dir / "cotizaciones.json")
    config.HISTORIAL_PATH = str(datos_dir / "historial.json") # Necesario para ejecutar_transaccion
    config.COMISIONES_PATH = str(datos_dir / "comisiones.json") # Necesario para ejecutar_transaccion

    # Datos de prueba
    crear_archivo_json(config.BILLETERA_PATH, {
        "USDT": {"saldos": {"disponible": "0", "reservado": "4000"}}
    })
    crear_archivo_json(config.ORDENES_PENDIENTES_PATH, [{
        "id_orden": "1", "par": "BTC/USDT", "estado": "pendiente", "accion": "compra", 
        "tipo_orden": "limit", "precio_disparo": "40000", "moneda_reservada": "USDT",
        "cantidad_reservada": "4000", "moneda_destino": "BTC", "moneda_origen": "USDT",
        "cantidad_cripto_principal": "0.1"
    }])
    # Precio favorable para la compra límite
    crear_archivo_json(config.COTIZACIONES_PATH, [
        {"ticker": "BTC", "precio_usd": "39000"},
        {"ticker": "USDT", "precio_usd": "1"}
    ])

    # Act: Ejecutar el motor
    verificar_y_ejecutar_ordenes_pendientes()

    # Assert: Verificar el estado final de los archivos
    ordenes_finales = cargar_ordenes_pendientes(config.ORDENES_PENDIENTES_PATH)
    billetera_final = cargar_billetera(config.BILLETERA_PATH)

    assert ordenes_finales[0]["estado"] == "ejecutada"
    assert billetera_final["USDT"]["saldos"]["reservado"] == Decimal("0")
    assert "BTC" in billetera_final
    assert billetera_final["BTC"]["saldos"]["disponible"] > 0