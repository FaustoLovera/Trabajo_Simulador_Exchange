# Simulador Exchange - **BlokX**

Este proyecto educativo fue desarrollado en el marco de la materia "Algoritmos y Estructuras de Datos I" de UADE, bajo la supervisión de la profesora Julia Monasterio.  
Su objetivo es aplicar los conocimientos de la cátedra simulando el funcionamiento básico de un exchange de criptomonedas.  
El sistema permite a los usuarios operar con saldo ficticio utilizando datos reales de cotización obtenidos de CoinGecko y Binance.

## 🎯 Objetivos del proyecto

- Familiarizar a los usuarios con el entorno de un exchange de criptomonedas.
- Simular operaciones de compra y venta mediante distintos tipos de órdenes: Market, Limit y Stop-Loss.
- Calcular y visualizar ganancias, pérdidas y balances del portafolio.
- Almacenar toda la información de manera local utilizando archivos `.json`.
- Comprender la interacción entre frontend y backend mediante una arquitectura moderna (HTML, CSS, Flask y Python).

## ⚙️ Funcionalidades

### Panel general de cotizaciones
- Visualización del top de criptomonedas con:
  - Nombre, ticker, precio, market cap, volumen, supply.
  - Variación en 1h, 24h y 7 días.
- Actualización automática de precios cada 15 segundos.

### Panel de trading
En este panel se verán tres secciones diferentes que contemplan lo necesario para ejecutar las ordenes de compra/venta.

#### Gráfico de velas japonesas
- Grafico en el cual se va a poder visualizar los diferentes pares de criptos usando Lightweight Charts (Libreria de JavaScript), en diferentes time frames: 1m, 5m, 15m, 1h, 4hs, 1d y 1w.

#### Órdenes
- Compra y venta de activos con órdenes:
  - Market
  - Limit
  - Stop-loss
- Comisión fija del 0.5% por transacción.
- Validaciones de saldo y tenencias disponibles.

#### Historial
- Registro de todas las operaciones realizadas.
- Incluye tipo de orden, precio, cantidad, fecha y fee aplicado.
  
### Billetera
- Visualización de tenencias actuales:
  - Cantidad, precio promedio, valor actual, ganancia/pérdida por activo.
- Balance total del portafolio en USDT.

## 🧠 Cómo funciona el sistema

El sistema está diseñado bajo una arquitectura modular que separa responsabilidades:

- **Rutas (`rutas/`)**: contienen los blueprints de Flask, que responden a las URLs y renderizan las plantillas HTML.
- **Servicios (`servicios/`)**: implementan la lógica de negocio (por ejemplo, compra y venta de criptomonedas, cálculos de balances, renderizado dinámico de fragmentos).
- **Acceso a datos (`acceso_datos/`)**: se encargan de leer y escribir archivos JSON, simulando una base de datos local.
- **Frontend (`frontend/`)**: contiene el HTML, CSS y JavaScript para la interfaz del usuario, incluyendo gráficos interactivos y recarga dinámica de datos.

### Flujo general

1. Al ingresar a la app, se cargan cotizaciones reales desde CoinGecko.
2. El usuario puede:
   - Consultar cotizaciones (actualizadas cada 15 segundos).
   - Ingresar al panel de trading y operar.
   - Visualizar su billetera y el historial de operaciones.
3. Toda la información es persistida automáticamente en archivos `.json`.

## 🗃️ Estructura del proyecto

```
simulador_exchange/
├── backend/
│   ├── app.py                      # Servidor Flask y punto de entrada
│   ├── config.py                   # Configuración del sistema y constantes globales
│   ├── rutas/                      # Blueprints que definen las vistas
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── trading_vista.py
│   │   ├── billetera_vista.py
│   │   └── api_externa.py
│   ├── servicios/                  # Lógica de negocio de cada módulo
│   │   ├── api_cotizaciones.py
│   │   ├── cotizaciones.py
│   │   ├── estado_billetera.py
│   │   ├── trading_logica.py
│   │   └── velas_logica.py
│   ├── acceso_datos/              # Acceso y manipulación de archivos .json
│   │   ├── datos_billetera.py
│   │   ├── datos_cotizaciones.py
│   │   └── datos_historial.py
│   └── utils/                     # Utilidades auxiliares
│       └── formateo_decimales.py
│
├── frontend/
│   ├── templates/                 # Plantillas HTML renderizadas por Flask
│   │   ├── index.html
│   │   ├── billetera.html
│   │   ├── trading.html
│   │   ├── fragmento_billetera.html
│   │   ├── fragmento_formulario_trading.html
│   │   ├── fragmento_historial.html
│   │   ├── fragmento_mensajes_flash.html
│   │   └── fragmento_tabla.html
│   └── static/                    # Archivos estáticos
│       ├── css/
│       │   ├── styles_index.css
│       │   └── styles_trading.css
│       ├── img/
│       │   └── logo_BlocX.png
│       └── js/
│           ├── funciones.js
│           └── grafico_velas.js
│
├── datos/                         # Archivos de persistencia
│   ├── billetera.json
│   ├── datos_cotizaciones.json
│   ├── datos_velas.json
│   └── historial_operaciones.json
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Cómo ejecutar el proyecto

### 1. Crear entorno virtual (recomendado)
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Iniciar la app
```bash
python3 app.py
```

Y luego acceder desde el navegador a:  
```
http://localhost:5000
```

## 📦 Tecnologías utilizadas

- Python 3.13
- Flask
- HTML, CSS, JavaScript
- Lightweight Charts (TradingView)

## 📌 Notas

- Todos los datos se almacenan localmente en formato JSON.
- No se requiere conexión a bases de datos externas.
- El sistema está pensado para ser didáctico y extensible.

---

**Grupo 12**  
Fausto Lovera — Patricio Menta — Andrei Veis
