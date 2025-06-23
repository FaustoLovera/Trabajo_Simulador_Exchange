# backend/acceso_datos/datos_ordenes.py

"""
Módulo de Acceso a Datos para las Órdenes Pendientes.

Este módulo se encarga de la persistencia de las órdenes de trading que no se
ejecutan de inmediato (Límite, Stop-Loss) y que están a la espera de que se
cumplan ciertas condiciones de mercado.
"""
import json
import os
from config import ORDENES_PENDIENTES_PATH


def cargar_ordenes_pendientes() -> list[dict]:
    """
    Carga la lista de órdenes pendientes desde el archivo JSON.

    Si el archivo no existe o está vacío, devuelve una lista vacía.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada uno es una orden pendiente.
    """
    # Asegura que el directorio exista
    os.makedirs(os.path.dirname(ORDENES_PENDIENTES_PATH), exist_ok=True)
    
    if not os.path.exists(ORDENES_PENDIENTES_PATH) or os.path.getsize(ORDENES_PENDIENTES_PATH) == 0:
        return []

    try:
        with open(ORDENES_PENDIENTES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: No se pudo leer o el archivo '{ORDENES_PENDIENTES_PATH}' está corrupto.")
        return []


def guardar_ordenes_pendientes(lista_ordenes: list[dict]):
    """
    Guarda la lista completa de órdenes pendientes en el archivo JSON.

    Esta función sobrescribe el archivo con la lista proporcionada. Se utiliza
    para actualizar el estado de las órdenes (ej. de 'pendiente' a 'ejecutada').

    Args:
        lista_ordenes (list[dict]): La lista completa de órdenes a guardar.
    """
    # Asegura que el directorio exista
    os.makedirs(os.path.dirname(ORDENES_PENDIENTES_PATH), exist_ok=True)

    with open(ORDENES_PENDIENTES_PATH, "w", encoding="utf-8") as f:
        json.dump(lista_ordenes, f, indent=4)


def agregar_orden_pendiente(nueva_orden: dict):
    """
    Añade una nueva orden a la lista de órdenes pendientes y la guarda.

    Args:
        nueva_orden (dict): El diccionario que representa la nueva orden a agregar.
    """
    ordenes = cargar_ordenes_pendientes()
    ordenes.append(nueva_orden)
    guardar_ordenes_pendientes(ordenes)