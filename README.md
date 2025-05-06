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



## 🗃️ Estructura del proyecto

```
simulador_exchange/
├── backend/                       # Código Python del servidor
│   ├── app.py                        # Servidor Flask y rutas principales
│   ├── config.py                     # Configuración de rutas de archivos, URLs, y ajustes 
│   ├── api_cotizaciones.py           # API para obtener cotizaciones de criptomonedas
│   ├── billetera.py                  # Funciones para operar con la billetera
│   ├── compra_y_venta.py             # Funciones para realizar operaciones de compra y venta
│   ├── guardar_datos_cotizaciones.py # Funciones para guardar datos de cotizaciones en archivos locales
│   └── tabla_cotizaciones.py         # Funciones para generar la tabla de cotizaciones en el frontend
│
├── frontend/
│   ├── templates/         # Archivos HTML (renderizados por Flask)
│   │   ├── index.html         # Pantalla principal con tabla de cotizaciones
│   │   ├── billetera.html     # Pantalla de billetera con datos de tenencias actuales
│   │   └── trading.html       # Pantalla de trading con gráfico de velas, sección de órdenes e historial
│   │
│   └── static/            # Archivos estáticos (CSS/JS)
│       ├── css/
│       │   ├── styles_index.css
│       │   └── styles_trading.css
│       │
│       └── js/            
│           ├── billetera.js         # Funciones para mostrar los datos de billetera y el historial al respectivo .html
│           ├── funciones.js         # Funciones para traer las cotizaciones de datos_cotizaciones.json al index.html
│           └── grafico_velas.js     # Funciones para el gráfico de velas japonesas con LightWeight Charts
│
├── datos/                 # Archivos de persistencia (.json)
│   ├── billetera.json               # Almacena información sobre el saldo y las tenencias actuales de criptomonedas.
│   ├── datos_cotizaciones.json      # Contiene las cotizaciones actuales de diferentes criptomonedas.
│   ├── datos_velas.json             # Guarda los datos históricos de velas japonesas de criptomonedas.
│   └── historial_operaciones.json   # Registra todas las operaciones de compra y venta realizadas por el usuario.
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
