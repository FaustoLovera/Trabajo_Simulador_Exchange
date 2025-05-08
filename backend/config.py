import os
from decimal import getcontext, ROUND_HALF_DOWN

# Directorio base para archivos de datos
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datos")

# Asegurar que el directorio de datos exista
os.makedirs(BASE_DATA_DIR, exist_ok=True) 

# Rutas de archivos
COTIZACIONES_PATH = os.path.join(BASE_DATA_DIR, "datos_cotizaciones.json")
BILLETERA_PATH = os.path.join(BASE_DATA_DIR, "billetera.json")
HISTORIAL_PATH = os.path.join(BASE_DATA_DIR, "historial_operaciones.json")
VELAS_PATH = os.path.join(BASE_DATA_DIR, "datos_velas.json")

# Saldo inicial de la billetera en USDT
BALANCE_INICIAL_USDT = "10000"

# URLs de las APIs
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# Configuración de Flask
FLASK_SECRET_KEY = "clave_segura_para_flash"

# Configuración de APIs
CANTIDAD_CRIPTOMONEDAS = 100  # Cantidad de criptomonedas a obtener de CoinGecko
CANTIDAD_VELAS = 300  # Cantidad de velas a obtener de Binance

# Configuración global para cálculos con Decimal
getcontext().prec = 28  # Cantidad de decimales para todos los cálculos
getcontext().rounding = ROUND_HALF_DOWN  # Redondeo hacia abajo (truncamiento)
