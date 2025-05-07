import json
import os
from decimal import Decimal
from config import COTIZACIONES_PATH, VELAS_PATH


def guardar_datos_cotizaciones(data):
    """
    Guarda los datos de las cotizaciones de criptomonedas en un archivo JSON. 
    Crea la carpeta necesaria si no existe y escribe los datos proporcionados 
    en el archivo definido por `COTIZACIONES_PATH`. Si ocurre algún error 
    durante el proceso, muestra un mensaje de error.

    La función también imprime información sobre el proceso de guardado,
    incluyendo la cantidad de criptomonedas a guardar y la ruta del archivo.
    """
    
    os.makedirs(os.path.dirname(COTIZACIONES_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_cotizaciones.json...")
    print(f"Cantidad de criptos a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(COTIZACIONES_PATH))

    try:
        with open(COTIZACIONES_PATH, "w") as archivo:
            json.dump(data, archivo, indent=4, default=lambda o: float(o) if isinstance(o, Decimal) else o)
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)


def cargar_datos_cotizaciones():
    """
    Carga los datos de las cotizaciones de criptomonedas desde un archivo JSON. 
    Si el archivo no existe, devuelve una lista vacía. Si el archivo está disponible, 
    lee su contenido y lo devuelve como un objeto Python.

    La función busca el archivo definido por `COTIZACIONES_PATH` y, si está presente, 
    carga los datos en formato JSON.
    """
    
    if not os.path.exists(COTIZACIONES_PATH):
        return []
    with open(COTIZACIONES_PATH, "r") as archivo:
        return json.load(archivo)


def guardar_datos_velas(data):
    """
    Guarda los datos de las velas de criptomonedas en un archivo JSON. 
    Crea la carpeta necesaria si no existe y escribe los datos proporcionados 
    en el archivo definido por `VELAS_PATH`. Si ocurre algún error durante el proceso, 
    muestra un mensaje de error.

    La función también imprime información sobre el proceso de guardado,
    incluyendo la cantidad de velas a guardar y la ruta del archivo.
    """
    
    os.makedirs(os.path.dirname(VELAS_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_velas.json...")
    print(f"Cantidad de velas a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(VELAS_PATH))

    try:
        with open(VELAS_PATH, "w") as archivo:
            json.dump(data, archivo, indent=4, default=lambda o: float(o) if isinstance(o, Decimal) else o)
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)
