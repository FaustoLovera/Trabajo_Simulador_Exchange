# config.py
### MODIFICADO ###

import os
from decimal import getcontext, ROUND_HALF_DOWN, Decimal
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Base del proyecto y carpeta de datos
PROYECTO_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_DIR = os.path.join(PROYECTO_DIR, "datos")
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# Rutas de archivos JSON
COTIZACIONES_PATH = os.path.join(BASE_DATA_DIR, "cotizaciones.json")
BILLETERA_PATH = os.path.join(BASE_DATA_DIR, "billetera.json")
HISTORIAL_PATH = os.path.join(BASE_DATA_DIR, "historial.json")
VELAS_PATH = os.path.join(BASE_DATA_DIR, "velas.json")
COMISIONES_PATH = os.path.join(BASE_DATA_DIR, "comisiones.json")
ORDENES_PENDIENTES_PATH = os.path.join(BASE_DATA_DIR, "ordenes_pendientes.json")

# Configuración inicial de los USDT con los cuales inicializa la app
BALANCE_INICIAL_USDT = "10000"

# Comisión por trade
TASA_COMISION = Decimal("0.005")  # 0.5% de comisión

# Clave secreta para Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "clave_por_defecto_insegura")

# URLs de APIs
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# Parámetros de scraping
CANTIDAD_CRIPTOMONEDAS = 100
CANTIDAD_VELAS = 250

# --- CONFIGURACIÓN NUMÉRICA GLOBAL --- ### NUEVO ###
# Precisión para los cálculos intermedios de la librería Decimal
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN

# Precisión estándar para el almacenamiento y la visualización
# de cantidades de criptomonedas (8 decimales)
PRECISION_CRIPTOMONEDA = Decimal("0.00000001")

# Precisión de decimales 4 para valores en USD
PRECISION_USD = Decimal("0.0001")

# Umbrales para la lógica de "polvo" (saldos pequeños)
UMBRAL_POLVO_USD = Decimal("0.01") # Valor en USD por debajo del cual se considera polvo
UMBRAL_CASI_CERO = Decimal("0.00000001") # Cantidad por debajo de la cual se considera cero para ciertas validaciones