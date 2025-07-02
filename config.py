"""
Configuración centralizada para la aplicación de simulación de exchange.

Este módulo define todas las constantes, rutas de archivos y variables de configuración
necesarias para el funcionamiento del backend. Carga variables de entorno desde un
archivo .env y establece rutas dinámicas basadas en la ubicación del proyecto.
"""

import os
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env en la raíz del proyecto.
load_dotenv()

# --- Constantes de Dominio del Negocio ---

# Acciones de Trading: Definen las operaciones básicas que un usuario puede realizar.
ACCION_COMPRAR = "compra"
ACCION_VENDER = "venta"

# Tipos de Órdenes: Clasifican las órdenes según su mecanismo de ejecución.
TIPO_ORDEN_MERCADO = "market"      # Se ejecuta al mejor precio de mercado actual.
TIPO_ORDEN_LIMITE = "limit"        # Se ejecuta a un precio específico o mejor.
TIPO_ORDEN_STOP_LIMIT = "stop-limit"  # Se convierte en una orden límite cuando se alcanza un precio de stop.

# Estados de Órdenes: Representan el ciclo de vida de una orden.
ESTADO_PENDIENTE = "pendiente"
ESTADO_EJECUTADA = "ejecutada"
ESTADO_CANCELADA = "cancelada"
ESTADO_ERROR = "error"

# --- Configuración del Sistema de Archivos ---

# Directorio base del proyecto y de la carpeta de datos para persistencia.
PROYECTO_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA_DIR = os.path.join(PROYECTO_DIR, "datos")
os.makedirs(BASE_DATA_DIR, exist_ok=True)  # Asegura que el directorio de datos exista.

# Rutas absolutas a los archivos JSON que actúan como base de datos.
COTIZACIONES_PATH = os.path.join(BASE_DATA_DIR, "cotizaciones.json")
BILLETERA_PATH = os.path.join(BASE_DATA_DIR, "billetera.json")
HISTORIAL_PATH = os.path.join(BASE_DATA_DIR, "historial.json")
VELAS_PATH = os.path.join(BASE_DATA_DIR, "velas.json")
COMISIONES_PATH = os.path.join(BASE_DATA_DIR, "comisiones.json")
ORDENES_PENDIENTES_PATH = os.path.join(BASE_DATA_DIR, "ordenes_pendientes.json")

# --- Parámetros de Simulación ---

# Balance inicial en USDT con el que la billetera del usuario comienza.
BALANCE_INICIAL_USDT = "10000"

# Tasa de comisión aplicada a cada operación de trading (compra o venta).
TASA_COMISION = Decimal("0.005")  # Representa una comisión del 0.5%.

# --- Configuración de la Aplicación Web (Flask) ---

# Clave secreta para firmar sesiones de Flask. Es crucial para la seguridad.
# Se carga desde variables de entorno o usa un valor por defecto inseguro (solo para desarrollo).
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
