"""Módulo para la persistencia de órdenes de trading pendientes.

Este módulo gestiona el ciclo de vida (lectura, escritura y modificación)
 de las órdenes pendientes (ej. Límite, Stop-Loss), usando un archivo JSON
 como mecanismo de almacenamiento.
"""
import json
import os
from typing import Optional
import config

def cargar_ordenes_pendientes(ruta_archivo: Optional[str] = None) -> list[dict]:
    """Carga la lista de órdenes pendientes desde un archivo JSON.

    Si el archivo no existe, está vacío o es ilegible, devuelve una lista
    vacía como fallback seguro.

    Args:
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta de `config.ORDENES_PENDIENTES_PATH`.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada uno es una orden.

    Side Effects:
        - Crea el directorio para el archivo si este no existe.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.ORDENES_PENDIENTES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto. Error: {e}")
        return []

def guardar_ordenes_pendientes(lista_ordenes: list[dict], ruta_archivo: Optional[str] = None):
    """Sobrescribe el archivo de órdenes con la lista proporcionada.

    ADVERTENCIA: Esta función reemplaza completamente el contenido del archivo.
    Debe usarse con cuidado para no perder datos.

    Args:
        lista_ordenes (list[dict]): La lista completa de órdenes a guardar.
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta de `config.ORDENES_PENDIENTES_PATH`.

    Side Effects:
        - Crea el directorio si no existe.
        - Escribe en el archivo, reemplazando su contenido.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.ORDENES_PENDIENTES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    try:
        with open(ruta_efectiva, "w", encoding="utf-8") as f:
            json.dump(lista_ordenes, f, indent=4)
    except Exception as e:
        print(
            f"Advertencia: No se pudo guardar el archivo de órdenes en '{ruta_efectiva}'. Error: {e}"
        )

def agregar_orden_pendiente(nueva_orden: dict, ruta_archivo: Optional[str] = None):
    """Añade una nueva orden al final de la lista de pendientes.

    Implementa un ciclo de "leer-modificar-escribir": carga todas las órdenes,
    añade la nueva y vuelve a guardar la lista completa. No es una operación
    de bajo nivel optimizada para rendimiento.

    Args:
        nueva_orden (dict): La orden a añadir.
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta de `config.ORDENES_PENDIENTES_PATH`.
    """
    ordenes = cargar_ordenes_pendientes(ruta_archivo=ruta_archivo)
    ordenes.append(nueva_orden)
    guardar_ordenes_pendientes(ordenes, ruta_archivo=ruta_archivo)