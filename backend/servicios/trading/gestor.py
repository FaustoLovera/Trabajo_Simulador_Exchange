# backend/servicios/trading/gestor.py

from datetime import datetime
from typing import Tuple

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.utils.utilidades_numericas import a_decimal

# --- Punto de Entrada Público ---

def cancelar_orden_pendiente(id_orden_a_cancelar: str) -> Tuple[bool, str]:
    """Busca una orden pendiente por su ID, la cancela, y libera los fondos reservados."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    orden_encontrada = next((o for o in todas_las_ordenes if o.get("id_orden") == id_orden_a_cancelar), None)
            
    if not orden_encontrada: return False, f"❌ No se encontró una orden con el ID {id_orden_a_cancelar}."
    if orden_encontrada.get("estado") != "pendiente": return False, f"❌ La orden {id_orden_a_cancelar} ya no está pendiente."

    billetera = cargar_billetera()
    moneda_origen = orden_encontrada["moneda_origen"]
    cantidad_reservada = a_decimal(orden_encontrada["cantidad_origen"])
    activo_origen = billetera.get(moneda_origen)

    if not activo_origen or a_decimal(activo_origen["saldos"].get("reservado")) < cantidad_reservada:
        orden_encontrada["estado"] = "error_cancelacion"
        guardar_ordenes_pendientes(todas_las_ordenes)
        return False, "❌ Error de consistencia: Los fondos reservados no existen."

    activo_origen["saldos"]["reservado"] -= cantidad_reservada
    activo_origen["saldos"]["disponible"] += cantidad_reservada
    orden_encontrada.update({"estado": "cancelada", "timestamp_cancelacion": datetime.now().isoformat()})
    
    guardar_billetera(billetera)
    guardar_ordenes_pendientes(todas_las_ordenes)
    
    return True, f"✅ Orden {orden_encontrada['par']} cancelada correctamente."