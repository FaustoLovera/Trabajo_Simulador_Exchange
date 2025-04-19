
import json
import os

def cargar_datos_billetera():
    ruta_archivo = os.path.join("data", "billetera.json")
    with open(ruta_archivo, "r") as archivo:
        datos = json.load(archivo)
    return datos

def estado_actual_completo():
    with open("./datos/billetera.json", "r") as f:
        data = json.load(f)

    # Eliminar monedas con valores residuales menores a un umbral
    data = {k: v for k, v in data.items() if v >= 0.000001}

    total_usdt = sum(data.values())
    detalle = {}
    for moneda, cantidad in data.items():
        porcentaje = (cantidad / total_usdt) * 100 if total_usdt > 0 else 0
        detalle[moneda] = {
            "cantidad": cantidad,
            "porcentaje": porcentaje
        }
    return detalle

