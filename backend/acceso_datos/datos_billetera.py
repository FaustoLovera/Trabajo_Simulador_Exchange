import json
import os
from decimal import Decimal, InvalidOperation
from config import BILLETERA_PATH, BALANCE_INICIAL_USDT


def cargar_billetera():
    """
    Carga la billetera desde el archivo JSON de forma segura.
    Si el archivo no existe, está vacío o corrupto, crea una billetera inicial.
    """
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    if not os.path.exists(BILLETERA_PATH) or os.path.getsize(BILLETERA_PATH) == 0:
        billetera_inicial = {"USDT": Decimal(BALANCE_INICIAL_USDT)}
        guardar_billetera(billetera_inicial)
        return billetera_inicial

    try:
        with open(BILLETERA_PATH, "r", encoding="utf-8") as f:
            datos_cargados = json.load(f)
            # Convierte todos los valores a Decimal, manejando posibles errores
            billetera = {}
            for ticker, cantidad_str in datos_cargados.items():
                try:
                    billetera[ticker] = Decimal(str(cantidad_str))
                except InvalidOperation:
                    print(
                        f"Advertencia: Valor inválido para {ticker} en billetera.json. Se usará 0."
                    )
                    billetera[ticker] = Decimal("0")
            return billetera
    except (json.JSONDecodeError, FileNotFoundError):
        print(
            f"Advertencia: Archivo '{BILLETERA_PATH}' corrupto. Se reiniciará la billetera."
        )
        billetera_inicial = {"USDT": Decimal(BALANCE_INICIAL_USDT)}
        guardar_billetera(billetera_inicial)
        return billetera_inicial


def guardar_billetera(billetera):
    """
    Guarda el estado de la billetera en el archivo JSON.
    Convierte los valores Decimal a string para preservar la precisión.
    """
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    # Prepara la billetera para ser guardada, convirtiendo Decimal a string
    billetera_serializable = {
        ticker: str(cantidad) for ticker, cantidad in billetera.items()
    }

    with open(BILLETERA_PATH, "w", encoding="utf-8") as f:
        json.dump(billetera_serializable, f, indent=4)
