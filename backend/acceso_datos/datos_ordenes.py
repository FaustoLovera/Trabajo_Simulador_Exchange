# backend/acceso_datos/datos_ordenes.py

"""
Módulo de Acceso a Datos para las Órdenes Pendientes.

Este módulo se encarga de la persistencia de las órdenes de trading que no se
ejecutan de inmediato (Límite, Stop-Loss) y que están a la espera de que se
cumplan ciertas condiciones de mercado.
"""
import json
import os
from typing import Optional
from config import ORDENES_PENDIENTES_PATH

def cargar_ordenes_pendientes(ruta_archivo: Optional[str] = None) -> list[dict]:
    """
    Carga la lista de órdenes pendientes desde el archivo JSON.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else ORDENES_PENDIENTES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto.")
        return []

def guardar_ordenes_pendientes(lista_ordenes: list[dict], ruta_archivo: Optional[str] = None):
    """
    Guarda la lista completa de órdenes pendientes en el archivo JSON.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else ORDENES_PENDIENTES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    with open(ruta_efectiva, "w", encoding="utf-8") as f:
        json.dump(lista_ordenes, f, indent=4)

def agregar_orden_pendiente(nueva_orden: dict, ruta_archivo: Optional[str] = None):
    """
    Añade una nueva orden a la lista de órdenes pendientes y la guarda.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ordenes = cargar_ordenes_pendientes(ruta_archivo=ruta_archivo)
    ordenes.append(nueva_orden)
    guardar_ordenes_pendientes(ordenes, ruta_archivo=ruta_archivo)