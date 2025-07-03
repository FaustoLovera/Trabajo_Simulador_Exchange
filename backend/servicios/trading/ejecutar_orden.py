"""Módulo del Kernel Transaccional.

Este módulo contiene la lógica fundamental y atómica para la ejecución de una
transacción financiera. Su única función pública, `ejecutar_transaccion`,
realiza un conjunto de operaciones críticas que deben ocurrir juntas o no
ocurrir en absoluto para mantener la integridad de los datos.

Responsabilidades:
-   Calcular comisiones.
-   Modificar los saldos de la billetera en memoria.
-   Persistir el registro de la transacción en el historial.
-   Persistir el registro de la comisión generada.

Importante: Este módulo modifica el estado de la billetera en memoria, pero
no la guarda en disco. La persistencia de la billetera es responsabilidad
del servicio que invoca a este módulo (ej. `gestor`).
"""

from decimal import Decimal
from typing import Any, Dict, Tuple, Optional

from backend.acceso_datos.datos_comisiones import registrar_comision
from backend.acceso_datos.datos_cotizaciones import (
    cargar_datos_cotizaciones,
    obtener_precio,
)
from backend.acceso_datos.datos_historial import guardar_en_historial
from backend.utils.utilidades_numericas import a_decimal
import config

# --- Funciones Privadas del Módulo ---

def _crear_activo_si_no_existe(billetera: Dict[str, Any], ticker: str, ruta_cotizaciones: Optional[str] = None) -> None:
    """Asegura que un activo exista en la billetera, creándolo si es necesario.

    Esta función de utilidad se invoca antes de acreditar un saldo a una moneda
    que el usuario podría no poseer. Si la moneda no existe en la billetera,
    inicializa su estructura con saldos en cero para evitar errores.

    Args:
        billetera: El diccionario que representa la billetera del usuario.
        ticker: El símbolo del activo a verificar (ej. "BTC").

    Side Effects:
        Modifica el diccionario `billetera` en memoria si el activo no existe.
    """
    if ticker not in billetera:
        info_criptos = {c['ticker']: c for c in cargar_datos_cotizaciones(ruta_cotizaciones)}
        info_nueva_moneda = info_criptos.get(ticker, {"nombre": ticker})
        billetera[ticker] = {"nombre": info_nueva_moneda.get("nombre", ticker), "saldos": {"disponible": a_decimal("0"), "reservado": a_decimal("0")}}

# --- Punto de Entrada Público del Módulo ---

def ejecutar_transaccion(
    billetera: Dict[str, Any],
    moneda_origen: str,
    cantidad_origen_bruta: Decimal,
    moneda_destino: str,
    tipo_operacion_historial: str,
    es_orden_pendiente: bool = False,
    ruta_cotizaciones: Optional[str] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Ejecuta una transacción atómica, modificando el estado en memoria.

    Esta es la operación central del sistema de trading. Realiza los cálculos
    de intercambio y comisiones, actualiza la billetera en memoria y persiste
    los registros de historial y comisiones. No persiste la billetera.

    Args:
        billetera: El objeto de la billetera del usuario (se modifica in-place).
        moneda_origen: Ticker de la moneda que se gasta (ej. "USDT").
        cantidad_origen_bruta: Cantidad total a deducir del origen.
        moneda_destino: Ticker de la moneda que se recibe (ej. "BTC").
        tipo_operacion_historial: Descripción para el historial (ej. "COMPRA-MARKET").
        es_orden_pendiente: Si `True`, los fondos se deducen del saldo
            'reservado'. Si `False`, se usa el saldo 'disponible'.

    Returns:
        Una tupla `(éxito, detalles)` donde:
        - `éxito` es `True` si la transacción fue exitosa, `False` si no.
        - `detalles` es un diccionario con los resultados de la ejecución o
          un mensaje de error.

    Warning:
        Esta función tiene efectos secundarios importantes:
        - Modifica el diccionario `billetera` directamente.
        - Escribe en los archivos de historial y comisiones.
        - El llamador es responsable de guardar la billetera modificada.
    """
    precio_origen_usdt = obtener_precio(moneda_origen, ruta_archivo=ruta_cotizaciones)
    precio_destino_usdt = obtener_precio(moneda_destino, ruta_archivo=ruta_cotizaciones)

    if precio_origen_usdt is None or precio_destino_usdt is None:
        return False, {"error": "No se pudo obtener la cotización para ejecutar la transacción."}

    if precio_destino_usdt == 0:
        return False, {"error": "El precio del activo de destino no puede ser cero."}

    # 1. Calcular comisión y cantidades netas.
    # La comisión se calcula sobre la cantidad bruta de la moneda de origen.
    cantidad_comision = cantidad_origen_bruta * config.TASA_COMISION
    cantidad_origen_neta = cantidad_origen_bruta - cantidad_comision
    valor_neto_usd_final = cantidad_origen_neta * precio_origen_usdt
    cantidad_destino_neta_final = valor_neto_usd_final / precio_destino_usdt

    # 2. Actualizar saldos de la billetera (operación en memoria).
    # Se determina si los fondos provienen del saldo disponible (órdenes de mercado)
    # o del saldo reservado (órdenes límite/stop que se están ejecutando).
    saldo_a_modificar = "reservado" if es_orden_pendiente else "disponible"
    billetera[moneda_origen]["saldos"][saldo_a_modificar] -= cantidad_origen_bruta

    _crear_activo_si_no_existe(billetera, moneda_destino, ruta_cotizaciones)
    billetera[moneda_destino]["saldos"]["disponible"] += cantidad_destino_neta_final

    # 3. Registrar la transacción y la comisión (operaciones de persistencia).
    registrar_comision(
        moneda_origen, cantidad_comision, cantidad_comision * precio_origen_usdt
    )
    guardar_en_historial(
        tipo_operacion_historial,
        moneda_origen,
        cantidad_origen_neta,
        moneda_destino,
        cantidad_destino_neta_final,
        valor_neto_usd_final,
    )

    # 4. Devolver los detalles de la ejecución para que el llamador los use.
    detalles_ejecucion = {
        "cantidad_destino_final": cantidad_destino_neta_final,
        "cantidad_origen_neta": cantidad_origen_neta,
        "cantidad_comision": cantidad_comision,
        "valor_usd_final": valor_neto_usd_final,
    }

    return True, detalles_ejecucion