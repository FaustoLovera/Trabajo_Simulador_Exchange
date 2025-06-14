# backend/acceso_datos/datos_historial.py
import json
import os # Necesitamos el módulo os para verificar el tamaño del archivo
from decimal import Decimal

RUTA_HISTORIAL = "datos/historial.json"

def cargar_historial():
    # Asegurarse de que el directorio existe
    os.makedirs(os.path.dirname(RUTA_HISTORIAL), exist_ok=True)
    
    # Verificar si el archivo existe y no está vacío
    if not os.path.exists(RUTA_HISTORIAL) or os.path.getsize(RUTA_HISTORIAL) == 0:
        return [] # Si el archivo no existe o está vacío, devuelve una lista vacía
    
    with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
        # Aquí puedes añadir un bloque try-except para manejar archivos JSON corruptos
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Si el archivo está corrupto (no vacío pero con JSON inválido),
            # puedes decidir si quieres:
            # 1. Devolver una lista vacía y sobrescribir el archivo corrupto al guardar.
            # 2. Levantar el error para depuración.
            # 3. Registrar el error y devolver []
            print(f"Advertencia: El archivo de historial '{RUTA_HISTORIAL}' está corrupto. Se reiniciará el historial.")
            return [] # O manejar el error de otra forma, como logs.

def guardar_en_historial(tipo, par, cantidad_destino, cantidad_origen, precio_relativo):
    historial = cargar_historial() # Carga el historial existente (o una lista vacía si no hay)

    # Convertir los Decimal a string para que json.dump pueda serializarlos
    operacion = {
        "timestamp": os.path.getmtime(RUTA_HISTORIAL), # Podrías usar datetime.now() para un timestamp más exacto de la operación
        "tipo": tipo,
        "par": par,
        "cantidad_destino": str(cantidad_destino),
        "cantidad_origen": str(cantidad_origen),
        "precio_relativo": str(precio_relativo)
    }
    historial.append(operacion)
    
    with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)