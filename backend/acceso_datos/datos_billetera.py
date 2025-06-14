import json
import os
from decimal import Decimal, InvalidOperation

RUTA_BILLETERA = "datos/billetera.json"

def cargar_billetera():
    """
    Carga el estado actual de la billetera desde el archivo JSON.
    Si el archivo no existe, está vacío o corrupto, lo inicializa.
    """
    # Asegurarse de que el directorio 'datos' existe
    os.makedirs(os.path.dirname(RUTA_BILLETERA), exist_ok=True)
    
    # Verificar si el archivo existe y no está vacío
    if not os.path.exists(RUTA_BILLETERA) or os.path.getsize(RUTA_BILLETERA) == 0:
        # Si el archivo no existe o está vacío, inicializa la billetera con 10000 USDT
        return {"USDT": Decimal("10000.00")} 
    
    with open(RUTA_BILLETERA, "r", encoding="utf-8") as f:
        try:
            billetera_data = json.load(f)
            # Asegurar que todas las cantidades se carguen como objetos Decimal
            for crypto, cantidad_str in billetera_data.items():
                try:
                    billetera_data[crypto] = Decimal(str(cantidad_str))
                except (InvalidOperation, TypeError):
                    # En caso de que el valor no sea válido, lo establecemos a 0.0
                    print(f"Advertencia: Saldo inválido para {crypto} en billetera.json. Establecido a 0.")
                    billetera_data[crypto] = Decimal("0.0") 
            return billetera_data
        except json.JSONDecodeError:
            # Si el archivo está corrupto (no vacío pero con JSON inválido), inicializa la billetera
            print(f"Advertencia: El archivo de billetera '{RUTA_BILLETERA}' está corrupto. Se inicializará la billetera.")
            return {"USDT": Decimal("10000.00")} 

def guardar_billetera(billetera):
    """
    Guarda el estado actual de la billetera en el archivo JSON.
    Convierte los objetos Decimal a string para su correcta serialización.
    """
    # Asegurarse de que el directorio 'datos' existe
    os.makedirs(os.path.dirname(RUTA_BILLETERA), exist_ok=True)

    # Convertir los valores Decimal a string antes de guardar para compatibilidad con JSON
    serializable_billetera = {}
    for crypto, cantidad in billetera.items():
        if isinstance(cantidad, Decimal):
            serializable_billetera[crypto] = str(cantidad)
        else:
            serializable_billetera[crypto] = cantidad # Fallback, aunque idealmente todos deberían ser Decimal

    with open(RUTA_BILLETERA, "w", encoding="utf-8") as f:
        json.dump(serializable_billetera, f, indent=4) # indent=4 para una mejor legibilidad