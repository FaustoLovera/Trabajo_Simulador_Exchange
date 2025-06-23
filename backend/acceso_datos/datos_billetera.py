# backend/acceso_datos/datos_billetera.py

import json
import os
from decimal import Decimal, InvalidOperation
from config import BILLETERA_PATH, BALANCE_INICIAL_USDT


def cargar_billetera() -> dict[str, dict[str, Decimal]]:
    """
    Carga la billetera de criptomonedas desde un archivo JSON.

    Esta función ha sido actualizada para manejar una estructura de billetera más
    compleja que distingue entre saldo "disponible" y "reservado".

    - Si el archivo `billetera.json` no existe, está vacío o corrupto, se crea
      una nueva billetera con el saldo inicial de USDT.
    - **Compatibilidad hacia atrás:** Si detecta el formato antiguo (donde el saldo
      era un valor simple), lo migra automáticamente al nuevo formato
      `{"disponible": saldo, "reservado": "0"}`.

    Returns:
        dict[str, dict[str, Decimal]]: Un diccionario que representa la billetera.
            Las claves son los tickers (ej. "USDT"), y los valores son otro
            diccionario con las claves "disponible" y "reservado" como objetos Decimal.

    Example (new format):
        >>> billetera = cargar_billetera()
        >>> print(billetera['USDT']['disponible'])
        Decimal('9000.00')
    """
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    if not os.path.exists(BILLETERA_PATH) or os.path.getsize(BILLETERA_PATH) == 0:
        billetera_inicial = {
            "USDT": {"disponible": Decimal(BALANCE_INICIAL_USDT), "reservado": Decimal("0")}
        }
        guardar_billetera(billetera_inicial)
        return billetera_inicial

    try:
        with open(BILLETERA_PATH, "r", encoding="utf-8") as f:
            datos_cargados = json.load(f)

        billetera_migrada = {}
        for ticker, valor in datos_cargados.items():
            try:
                if isinstance(valor, dict) and "disponible" in valor:
                    billetera_migrada[ticker] = {
                        "disponible": Decimal(str(valor.get("disponible", "0"))),
                        "reservado": Decimal(str(valor.get("reservado", "0"))),
                    }
                else:
                    billetera_migrada[ticker] = {
                        "disponible": Decimal(str(valor)),
                        "reservado": Decimal("0"),
                    }
            except (InvalidOperation, TypeError):
                billetera_migrada[ticker] = {
                    "disponible": Decimal("0"),
                    "reservado": Decimal("0"),
                }

        if any(not isinstance(v, dict) for v in datos_cargados.values()):
             guardar_billetera(billetera_migrada)

        return billetera_migrada

    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: Archivo '{BILLETERA_PATH}' corrupto. Se reiniciará la billetera.")
        billetera_inicial = {
            "USDT": {"disponible": Decimal(BALANCE_INICIAL_USDT), "reservado": Decimal("0")}
        }
        guardar_billetera(billetera_inicial)
        return billetera_inicial


def guardar_billetera(billetera: dict[str, dict[str, Decimal]]):
    """
    Guarda el estado actual de la billetera en un archivo JSON.

    Esta función serializa la nueva estructura de billetera (con saldos disponible
    y reservado) a formato JSON, convirtiendo los valores Decimal a string
    para mantener la precisión.

    Args:
        billetera (dict[str, dict[str, Decimal]]): El diccionario de la billetera a guardar.
    """
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    billetera_serializable = {
        ticker: {
            "disponible": str(saldos["disponible"]),
            "reservado": str(saldos["reservado"]),
        }
        for ticker, saldos in billetera.items()
    }

    with open(BILLETERA_PATH, "w", encoding="utf-8") as f:
        json.dump(billetera_serializable, f, indent=4)