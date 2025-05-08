import json
from config import BILLETERA_PATH
from decimal import Decimal

def cargar_billetera():
    try:
        with open(BILLETERA_PATH, "r") as f:
            return {k: Decimal(v) for k, v in json.load(f).items()}
    except FileNotFoundError:
        return {}

def guardar_billetera(billetera):
    with open(BILLETERA_PATH, "w") as f:
        json.dump(billetera, f, indent=4, default=lambda o: format(o, 'f') if isinstance(o, Decimal) else o)