# backend/acceso_datos/datos_cotizaciones.py
import json
import os
from decimal import Decimal, InvalidOperation 

RUTA_COTIZACIONES = "datos/cotizaciones.json"

def cargar_datos_cotizaciones():
    """
    Carga todos los datos de cotizaciones desde el archivo JSON.
    Retorna una lista de diccionarios con las cotizaciones.
    Si el archivo no existe, está vacío o corrupto, retorna una lista vacía.
    """
    os.makedirs(os.path.dirname(RUTA_COTIZACIONES), exist_ok=True)

    if not os.path.exists(RUTA_COTIZACIONES) or os.path.getsize(RUTA_COTIZACIONES) == 0:
        print("DEBUG: cotizaciones.json no existe o está vacío. Inicializando con cotizaciones básicas.") 
        return [
            {"ticker": "USDT", "precio_usdt": Decimal("1.0")},
            # Puedes añadir otras criptos con precios por defecto aquí, ejemplo:
            # {"ticker": "BTC", "precio_usdt": Decimal("60000.00")},
            # {"ticker": "ETH", "precio_usdt": Decimal("3000.00")}
        ]

    try:
        with open(RUTA_COTIZACIONES, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if 'precio_usdt' in item:
                    try:
                        # CONVERSIÓN CLAVE: Aseguramos que sea Decimal al cargar
                        item['precio_usdt'] = Decimal(str(item['precio_usdt'])) 
                    except (InvalidOperation, TypeError):
                        item['precio_usdt'] = Decimal('0.0') 
            return data
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo de cotizaciones '{RUTA_COTIZACIONES}' está corrupto. Se retornará una lista con USDT.")
        return [
            {"ticker": "USDT", "precio_usdt": Decimal("1.0")} 
        ]
    except Exception as e:
        print(f"Error inesperado al cargar cotizaciones desde '{RUTA_COTIZACIONES}': {e}")
        return [
            {"ticker": "USDT", "precio_usdt": Decimal("1.0")} 
        ]

def obtener_precio(ticker):
    """
    Obtiene el precio en USDT de una criptomoneda específica.
    Retorna el precio como Decimal o None si el ticker no se encuentra.
    """
    cotizaciones = cargar_datos_cotizaciones()
    for c in cotizaciones:
        if c.get("ticker") == ticker:
            # CONVERSIÓN CLAVE AQUÍ: Aseguramos que el valor devuelto sea SIEMPRE un Decimal.
            try:
                return Decimal(str(c.get("precio_usdt", Decimal('0.0'))))
            except (InvalidOperation, TypeError):
                return Decimal('0.0') 

    return None

def guardar_cotizaciones(data):
    """
    Guarda los datos de cotizaciones en el archivo JSON.
    Convierte los objetos Decimal a string para su correcta serialización.
    """
    os.makedirs(os.path.dirname(RUTA_COTIZACIONES), exist_ok=True)

    serializable_data = []
    for item in data:
        serializable_item = item.copy() 
        if 'precio_usdt' in serializable_item and isinstance(serializable_item['precio_usdt'], Decimal):
            serializable_item['precio_usdt'] = str(serializable_item['precio_usdt'])
        serializable_data.append(serializable_item)

    with open(RUTA_COTIZACIONES, "w", encoding="utf-8") as f:
        json.dump(serializable_data, f, indent=4)