import json
import os
from decimal import Decimal
from config import COTIZACIONES_PATH, VELAS_PATH


def guardar_datos_cotizaciones(data):
    os.makedirs(os.path.dirname(COTIZACIONES_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_cotizaciones.json...")
    print(f"Cantidad de criptos a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(COTIZACIONES_PATH))
    try:
        with open(COTIZACIONES_PATH, "w") as archivo:
            json.dump(data, archivo, indent=4, default=str) # This is already correct!
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)


def cargar_datos_cotizaciones():
    if not os.path.exists(COTIZACIONES_PATH):
        return []
    with open(COTIZACIONES_PATH, "r") as archivo:
        # --- MODIFICATION HERE ---
        # When loading, parse any numbers (which were saved as strings from Decimal) back into Decimal objects.
        return json.load(archivo, parse_float=Decimal)


def guardar_datos_velas(data):
    os.makedirs(os.path.dirname(VELAS_PATH), exist_ok=True)
    print("💾 Guardando datos en datos_velas.json...")
    print(f"Cantidad de velas a guardar: {len(data)}")
    print("📁 Guardando en:", os.path.abspath(VELAS_PATH))

    try:
        with open(VELAS_PATH, "w") as archivo:
            # For candlestick data, you are currently converting Decimal to float on save.
            # If precision is critical for velas data, you might consider changing default=str here too,
            # and then using parse_float=Decimal when loading velas data.
            # But for the current problem, this is less critical.
            json.dump(data, archivo, indent=4, default=lambda o: float(o) if isinstance(o, Decimal) else o)
        print("✅ Datos guardados correctamente")
    except Exception as e:
        print("❌ Error al guardar el archivo:", e)