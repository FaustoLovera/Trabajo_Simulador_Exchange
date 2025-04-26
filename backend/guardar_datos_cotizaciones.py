import json
import os

RUTA_COTIZACIONES = "./datos/datos_cotizaciones.json"
RUTA_VELAS = "./datos/datos_velas.json"


def guardar_datos_cotizaciones(data):
    os.makedirs(os.path.dirname(RUTA_COTIZACIONES), exist_ok=True)
    print("💾 Guardando datos en datos_cotizaciones.json...")
    print(f"Cantidad de criptos a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(RUTA_COTIZACIONES))

    try:
        with open(RUTA_COTIZACIONES, "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)


def cargar_datos_cotizaciones():
    if not os.path.exists(RUTA_COTIZACIONES):
        return []
    with open(RUTA_COTIZACIONES, "r") as archivo:
        return json.load(archivo)


def guardar_datos_velas(data):
    os.makedirs(os.path.dirname(RUTA_VELAS), exist_ok=True)
    print("💾 Guardando datos en datos_velas.json...")
    print(f"Cantidad de velas a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(RUTA_VELAS))

    try:
        with open(RUTA_VELAS, "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)
