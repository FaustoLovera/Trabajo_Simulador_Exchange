

from datetime import datetime
from typing import Dict

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.utils.utilidades_numericas import a_decimal


def cancelar_orden_pendiente(id_orden_a_cancelar: str) -> Dict:
    """
    ### REFACTORIZADO ### - Devuelve un único diccionario de resultados.
    La presencia de la clave 'error' determina el fallo.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    orden_encontrada = next((o for o in todas_las_ordenes if o.get("id_orden") == id_orden_a_cancelar), None)
            
    if not orden_encontrada:
        return {"error": f"No se encontró una orden con el ID {id_orden_a_cancelar}."}
    
    if orden_encontrada.get("estado") != "pendiente":
        return {"error": f"La orden {id_orden_a_cancelar} ya no está pendiente y no puede ser cancelada."}

    billetera = cargar_billetera()
    
    moneda_reservada = orden_encontrada["moneda_reservada"]
    cantidad_reservada = a_decimal(orden_encontrada["cantidad_reservada"])
    
    activo_a_liberar = billetera.get(moneda_reservada)

    if not activo_a_liberar or a_decimal(activo_a_liberar["saldos"].get("reservado")) < cantidad_reservada:
        orden_encontrada["estado"] = "error_cancelacion"
        orden_encontrada["mensaje_error"] = "Error de consistencia: los fondos a liberar no se encontraron en la billetera."
        guardar_ordenes_pendientes(todas_las_ordenes)
        return {"error": "Error de consistencia en la billetera. No se pudieron liberar los fondos."}

    activo_a_liberar["saldos"]["reservado"] -= cantidad_reservada
    activo_a_liberar["saldos"]["disponible"] += cantidad_reservada
    
    orden_encontrada.update({
        "estado": "cancelada",
        "timestamp_cancelacion": datetime.now().isoformat()
    })
    
    guardar_billetera(billetera)
    guardar_ordenes_pendientes(todas_las_ordenes)
    
    mensaje_exito = f"Orden {orden_encontrada['par']} cancelada. Se liberaron {formato_cantidad_cripto(cantidad_reservada)} {moneda_reservada}."
    
    return {"mensaje": mensaje_exito, "datos": orden_encontrada}
