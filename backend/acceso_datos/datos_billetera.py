import json
import os
from decimal import Decimal, InvalidOperation
from config import BILLETERA_PATH, BALANCE_INICIAL_USDT


def cargar_billetera():
    """
    Carga la billetera de criptomonedas desde un archivo JSON.

    Esta función se encarga de leer el archivo `billetera.json`. Si el archivo no existe,
    está vacío o contiene datos corruptos, se crea una nueva billetera con un saldo
    inicial de USDT, definido por `BALANCE_INICIAL_USDT`.

    Maneja de forma segura la conversión de los saldos de texto a objetos Decimal
    para mantener la precisión en los cálculos financieros.

    Returns:
        dict[str, Decimal]: Un diccionario que representa la billetera.
                            Las claves son los tickers de las criptomonedas (ej. "USDT", "BTC")
                            y los valores son las cantidades como objetos Decimal.

    Example:
        >>> # Suponiendo que el archivo de billetera no existe o está vacío.
        >>> billetera = cargar_billetera()
        >>> print(billetera)
        {'USDT': Decimal('10000')}
    """
    # Asegura que el directorio de la billetera exista.
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    # Si el archivo no existe o está vacío, crea una billetera inicial.
    if not os.path.exists(BILLETERA_PATH) or os.path.getsize(BILLETERA_PATH) == 0:
        billetera_inicial = {"USDT": Decimal(BALANCE_INICIAL_USDT)}
        guardar_billetera(billetera_inicial)
        return billetera_inicial

    try:
        with open(BILLETERA_PATH, "r", encoding="utf-8") as f:
            datos_cargados = json.load(f)

            billetera = {}
            # Convierte todos los valores a Decimal para mantener la precisión.
            for ticker, cantidad_str in datos_cargados.items():
                try:
                    billetera[ticker] = Decimal(str(cantidad_str))
                except InvalidOperation:
                    # Si un valor no es un número válido, se informa y se establece en 0.
                    print(
                        f"Advertencia: Valor inválido para {ticker} en billetera.json. Se usará 0."
                    )
                    billetera[ticker] = Decimal("0")
            return billetera
    except (json.JSONDecodeError, FileNotFoundError):
        # Si el archivo está corrupto o no se encuentra (aunque ya se verificó),
        # se reinicia la billetera para evitar errores en la aplicación.
        print(
            f"Advertencia: Archivo '{BILLETERA_PATH}' corrupto o no encontrado. Se reiniciará la billetera."
        )
        billetera_inicial = {"USDT": Decimal(BALANCE_INICIAL_USDT)}
        guardar_billetera(billetera_inicial)
        return billetera_inicial


def guardar_billetera(billetera):
    """
    Guarda el estado actual de la billetera en un archivo JSON.

    Esta función toma un diccionario que representa la billetera y lo serializa
    a formato JSON, guardándolo en la ruta especificada por `BILLETERA_PATH`.
    Los valores de tipo Decimal se convierten a string para evitar la pérdida de
    precisión durante la serialización.

    Args:
        billetera (dict[str, Decimal]): El diccionario de la billetera a guardar.
                                         Las claves son los tickers (ej. "BTC") y los valores
                                         son las cantidades en formato Decimal.

    Example:
        >>> mi_billetera = {'USDT': Decimal('5000.00'), 'BTC': Decimal('0.1')}
        >>> guardar_billetera(mi_billetera)
        # Esto creará o sobrescribirá billetera.json con:
        # {
        #     "USDT": "5000.00",
        #     "BTC": "0.1"
        # }
    """
    # Asegura que el directorio de la billetera exista antes de guardar.
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    # Convierte los valores Decimal a string para una serialización JSON segura y precisa.
    billetera_serializable = {
        ticker: str(cantidad) for ticker, cantidad in billetera.items()
    }

    with open(BILLETERA_PATH, "w", encoding="utf-8") as f:
        json.dump(billetera_serializable, f, indent=4)
