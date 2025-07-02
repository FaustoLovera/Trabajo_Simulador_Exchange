# --- FILENAME: tests/test_trading_gestor.py (VERSIÓN SIMPLIFICADA) ---
import pytest
import json
from decimal import Decimal

# Importar la función a probar
from backend.servicios.trading.gestor import cancelar_orden_pendiente
# Importar funciones de acceso a datos para verificar
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes
# Importar el módulo config para redirigir las rutas temporalmente
import config

def crear_archivo_json(ruta, contenido):
    """Función de ayuda para crear archivos JSON en los tests."""
    with open(ruta, 'w') as f:
        json.dump(contenido, f, indent=4)

def test_cancelacion_exitosa_con_archivos(tmp_path):
    """
    Prueba que una orden pendiente se cancela y los fondos se liberan,
    interactuando con archivos temporales.
    """
    # Arrange: Preparar el entorno de archivos temporales
    datos_dir = tmp_path / "datos"
    datos_dir.mkdir()
    config.BILLETERA_PATH = str(datos_dir / "billetera.json")
    config.ORDENES_PENDIENTES_PATH = str(datos_dir / "ordenes.json")
    # Para la llamada a estado_actual_completo
    config.HISTORIAL_PATH = str(datos_dir / "historial.json")
    config.COTIZACIONES_PATH = str(datos_dir / "cotizaciones.json")
    
    crear_archivo_json(config.BILLETERA_PATH, {
        "USDT": {"saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"saldos": {"disponible": "1.0", "reservado": "0.5"}}
    })
    crear_archivo_json(config.ORDENES_PENDIENTES_PATH, [
        {"id_orden": "btc_venta_1", "estado": "pendiente", "moneda_reservada": "BTC", "cantidad_reservada": "0.5", "par": "BTC/USDT"},
        {"id_orden": "eth_compra_1", "estado": "ejecutada", "moneda_reservada": "USDT", "cantidad_reservada": "1000"}
    ])
    # Archivos vacíos necesarios para estado_actual_completo
    crear_archivo_json(config.HISTORIAL_PATH, [])
    crear_archivo_json(config.COTIZACIONES_PATH, [])

    # Act
    resultado = cancelar_orden_pendiente("btc_venta_1")

    # Assert
    assert "error" not in resultado
    assert "Orden BTC/USDT cancelada" in resultado["mensaje"]
    
    # Verificar leyendo directamente los archivos modificados
    billetera_final = cargar_billetera(config.BILLETERA_PATH)
    ordenes_finales = cargar_ordenes_pendientes(config.ORDENES_PENDIENTES_PATH)
    
    # Fondos liberados
    assert billetera_final["BTC"]["saldos"]["reservado"] == Decimal("0")
    assert billetera_final["BTC"]["saldos"]["disponible"] == Decimal("1.5")
    
    # Estado de la orden cambiado
    orden_cancelada = next(o for o in ordenes_finales if o["id_orden"] == "btc_venta_1")
    assert orden_cancelada["estado"] == "cancelada"

def test_cancelar_orden_inexistente(tmp_path):
    """Prueba que falla al intentar cancelar una orden que no existe."""
    # Arrange: Solo necesitamos un archivo de órdenes vacío
    datos_dir = tmp_path / "datos"
    datos_dir.mkdir()
    config.ORDENES_PENDIENTES_PATH = str(datos_dir / "ordenes.json")
    crear_archivo_json(config.ORDENES_PENDIENTES_PATH, [])

    # Act
    resultado = cancelar_orden_pendiente("id_invalido")

    # Assert
    assert "error" in resultado
    assert "No se encontró una orden" in resultado["error"]