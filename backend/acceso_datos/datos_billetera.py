"""Módulo para la persistencia de datos de la billetera del usuario.

Este componente gestiona el ciclo completo de lectura y escritura del estado
de la billetera en un archivo JSON. Está diseñado para ser resiliente:
si el archivo no existe o está corrupto, se autogenera una billetera inicial
para garantizar la continuidad operativa de la aplicación.

Centraliza la lógica de serialización (Decimal -> str) y deserialización
(str -> Decimal), asegurando la integridad y precisión de los datos financieros.
"""

import json
import os
from typing import Dict, Optional

from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto
import config

def _crear_billetera_inicial() -> Dict[str, Dict]:
    """Genera la estructura de datos para una billetera nueva.

    Returns:
        Dict[str, Dict]: Un diccionario que representa el estado inicial de la
                         billetera, con un saldo inicial en USDT.
    """
    return {
        "USDT": {
            "nombre": "Tether",
            "saldos": {
                "disponible": a_decimal(config.BALANCE_INICIAL_USDT),
                "reservado": a_decimal("0")
            }
        }
    }

def cargar_billetera(ruta_archivo: Optional[str] = None) -> Dict[str, Dict]:
    """Carga la billetera desde un archivo JSON, creándola si es necesario.

    Este proceso es "autocorrectivo": si el archivo no existe, está vacío o
    corrupto, se genera una billetera inicial para asegurar que la aplicación
    siempre tenga un estado de billetera válido con el que operar.

    Args:
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta por defecto de la configuración.

    Returns:
        Dict[str, Dict]: Un diccionario que representa la billetera. Los saldos
                         se deserializan a objetos `Decimal` para permitir
                         cálculos precisos.

    Side Effects:
        - Crea el directorio y el archivo de la billetera si no existen.
        - Sobrescribe archivos corruptos o vacíos con una billetera nueva.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.BILLETERA_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        billetera_inicial = _crear_billetera_inicial()
        guardar_billetera(billetera_inicial, ruta_archivo=ruta_efectiva)
        return billetera_inicial

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            datos_cargados = json.load(f)
    except Exception as e:
                # Fallback: si el archivo está corrupto, se crea una billetera nueva
        # para asegurar la continuidad de la aplicación.
        print(f"Advertencia: Archivo '{ruta_efectiva}' corrupto o ilegible. Se reiniciará la billetera. Error: {e}")
        billetera_inicial = _crear_billetera_inicial()
        guardar_billetera(billetera_inicial, ruta_archivo=ruta_efectiva)
        return billetera_inicial

    # Deserialización: convierte los saldos de string (en JSON) a Decimal.
    billetera_final = {}
    for ticker, activo in datos_cargados.items():
        billetera_final[ticker] = {
            "nombre": activo.get("nombre", ticker),
            "saldos": {
                "disponible": a_decimal(activo.get("saldos", {}).get("disponible", "0")),
                "reservado": a_decimal(activo.get("saldos", {}).get("reservado", "0"))
            }
        }
    return billetera_final

def guardar_billetera(billetera: Dict[str, Dict], ruta_archivo: Optional[str] = None):
    """Guarda el estado de la billetera en un archivo JSON.

    Serializa el diccionario de la billetera a un formato JSON legible.
    Antes de guardar, los saldos (objetos `Decimal`) se cuantizan para
    asegurar una precisión estándar y luego se convierten a `str`.

    Args:
        billetera (Dict[str, Dict]): El objeto de la billetera a guardar.
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta por defecto de la configuración.

    Side Effects:
        - Crea el directorio de la billetera si no existe.
        - Sobrescribe completamente el archivo de la billetera en disco.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.BILLETERA_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    datos_para_json = {}
    for ticker, activo in billetera.items():
        saldos = activo.get("saldos", {})
        
        saldo_disponible = saldos.get("disponible", a_decimal(0))
        saldo_reservado = saldos.get("reservado", a_decimal(0))
        
        # 1. Cuantizar para asegurar la precisión estándar antes de guardar.
        saldo_disponible_q = cuantizar_cripto(saldo_disponible)
        saldo_reservado_q = cuantizar_cripto(saldo_reservado)

        # 2. Convertir a string para la serialización en JSON.
        str_disponible = str(saldo_disponible_q)
        str_reservado = str(saldo_reservado_q)
        
        datos_para_json[ticker] = {
            "nombre": activo.get("nombre", ticker),
            "saldos": {
                "disponible": str_disponible,
                "reservado": str_reservado,
            }
        }

    try:
        with open(ruta_efectiva, "w", encoding="utf-8") as f:
            json.dump(datos_para_json, f, indent=4)
    except Exception as e:
        # En un entorno de producción, esto debería ser manejado por un sistema de logging.
        print(f"Error Crítico: No se pudo guardar el archivo de billetera en '{ruta_efectiva}'. Error: {e}")