from decimal import Decimal
from typing import Dict

from backend.acceso_datos.datos_billetera import guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.acceso_datos.datos_historial import guardar_en_historial
from backend.acceso_datos.datos_comisiones import registrar_comision
from config import TASA_COMISION
from backend.utils.utilidades_numericas import a_decimal

# --- Funciones Privadas del Módulo ---

def _crear_activo_si_no_existe(billetera: dict, ticker: str):
    """Crea una entrada para un activo en la billetera si no existe."""
    if ticker not in billetera:
        info_criptos = {c['ticker']: c for c in cargar_datos_cotizaciones()}
        info_nueva_moneda = info_criptos.get(ticker, {"nombre": ticker})
        billetera[ticker] = {"nombre": info_nueva_moneda.get("nombre", ticker), "saldos": {"disponible": a_decimal("0"), "reservado": a_decimal("0")}}

# --- Punto de Entrada Público del Módulo ---

def ejecutar_transaccion(
    billetera: Dict,
    moneda_origen: str,
    cantidad_origen_bruta: Decimal,
    moneda_destino: str,
    tipo_operacion_historial: str,
    es_orden_pendiente: bool = False
) -> tuple[bool, dict]:
    """
    ### NUEVO - Función Atómica y Centralizada ###
    Ejecuta una transacción completa: calcula comisión, actualiza saldos,
    registra en historial y devuelve los detalles.
    
    Args:
        billetera: El objeto de la billetera actual.
        moneda_origen: Ticker de la moneda que se gasta.
        cantidad_origen_bruta: Cantidad total que se deduce del origen.
        moneda_destino: Ticker de la moneda que se recibe.
        tipo_operacion_historial: String para guardar en el historial (ej. "Compra", "limit-compra").
        es_orden_pendiente: True si los fondos vienen de 'reservado' en lugar de 'disponible'.

    Returns:
        Una tupla (éxito, diccionario_de_resultados).
    """
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)

    if not all([precio_origen_usdt, precio_destino_usdt, not precio_destino_usdt.is_zero()]):
        return False, {"error": "No se pudo obtener la cotización para ejecutar la transacción."}

    # 1. Calcular comisión y cantidades netas
    cantidad_comision = cantidad_origen_bruta * TASA_COMISION
    cantidad_origen_neta = cantidad_origen_bruta - cantidad_comision
    valor_neto_usd_final = cantidad_origen_neta * precio_origen_usdt
    cantidad_destino_neta_final = valor_neto_usd_final / precio_destino_usdt

    # 2. Actualizar saldos de la billetera
    saldo_a_modificar = "reservado" if es_orden_pendiente else "disponible"
    billetera[moneda_origen]["saldos"][saldo_a_modificar] -= cantidad_origen_bruta
    
    _crear_activo_si_no_existe(billetera, moneda_destino)
    billetera[moneda_destino]["saldos"]["disponible"] += cantidad_destino_neta_final
    
    # 3. Registrar comisión e historial
    registrar_comision(moneda_origen, cantidad_comision, cantidad_comision * precio_origen_usdt)
    guardar_en_historial(
        tipo_operacion_historial,
        moneda_origen,
        cantidad_origen_neta,
        moneda_destino,
        cantidad_destino_neta_final,
        valor_neto_usd_final
    )
    
    # 4. Devolver los detalles de la ejecución
    detalles_ejecucion = {
        "cantidad_destino_final": cantidad_destino_neta_final,
        "cantidad_origen_neta": cantidad_origen_neta,
        "cantidad_comision": cantidad_comision,
        "valor_usd_final": valor_neto_usd_final,
    }
    
    return True, detalles_ejecucion