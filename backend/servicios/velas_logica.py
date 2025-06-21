"""
Servicio para la persistencia de datos de mercado en archivos JSON.

Este módulo, aunque nombrado `velas_logica`, tiene la doble responsabilidad de
guardar y cargar tanto los datos de cotizaciones generales del mercado como los
datos específicos de velas (k-lines).
"""

import json
import os
from decimal import Decimal
from typing import Any
from config import COTIZACIONES_PATH, VELAS_PATH


def guardar_datos_cotizaciones(data: list[dict[str, Any]]):
    """
    Guarda los datos de cotizaciones de criptomonedas en un archivo JSON.

    Asegura que el directorio de destino exista y maneja la serialización
    de objetos Decimal a float para compatibilidad con JSON.

    Args:
        data (list[dict[str, Any]]): La lista de datos de cotizaciones a guardar.

    Side Effects:
        - Crea el directorio si no existe.
        - Escribe/sobrescribe el archivo `datos_cotizaciones.json`.
        - Imprime logs del proceso en la consola.
    """
    os.makedirs(os.path.dirname(COTIZACIONES_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_cotizaciones.json...")
    print(f"Cantidad de criptos a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(COTIZACIONES_PATH))

    try:
        with open(COTIZACIONES_PATH, "w") as archivo:
            json.dump(
                data,
                archivo,
                indent=4,
                default=lambda o: float(o) if isinstance(o, Decimal) else o,
            )
        print("✅ Datos guardados correctamente")
    except (IOError, TypeError) as e:
        print(f"❌ Error al guardar el archivo: {e}")


def cargar_datos_cotizaciones() -> list[dict[str, Any]]:
    """
    Carga los datos de cotizaciones desde el archivo JSON local.

    Returns:
        list[dict[str, Any]]: La lista de datos de cotizaciones. Retorna una lista
                              vacía si el archivo no existe.
    """
    if not os.path.exists(COTIZACIONES_PATH):
        return []
    try:
        with open(COTIZACIONES_PATH, "r") as archivo:
            return json.load(archivo)
    except (IOError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar datos de cotizaciones: {e}")
        return []


def guardar_datos_velas(data: list[dict[str, Any]]):
    """
    Guarda los datos de velas (k-lines) de una criptomoneda en un archivo JSON.

    Args:
        data (list[dict[str, Any]]): La lista de datos de velas a guardar.

    Side Effects:
        - Crea el directorio si no existe.
        - Escribe/sobrescribe el archivo `datos_velas.json`.
        - Imprime logs del proceso en la consola.
    """
    os.makedirs(os.path.dirname(VELAS_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_velas.json...")
    print(f"Cantidad de velas a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(VELAS_PATH))

    try:
        with open(VELAS_PATH, "w") as archivo:
            json.dump(
                data,
                archivo,
                indent=4,
                default=lambda o: float(o) if isinstance(o, Decimal) else o,
            )
        print("✅ Datos guardados correctamente")
    except (IOError, TypeError) as e:
        print(f"❌ Error al guardar el archivo: {e}")
