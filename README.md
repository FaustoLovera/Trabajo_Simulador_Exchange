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

El sistema está diseñado bajo una arquitectura desacoplada que separa claramente las responsabilidades del backend y del frontend:

- **Backend (Python/Flask)**: Actúa como una API pura de JSON. Sus responsabilidades son:
    - **`rutas/`**: Define los endpoints de la API (`/api/...`) que exponen los datos y la lógica de negocio en formato JSON. También sirve el contenedor HTML inicial de cada página.
    - **`servicios/`**: Contiene toda la lógica de negocio (cálculos de billetera, procesamiento de órdenes, formato de datos) y prepara los datos para ser enviados como JSON.
    - **`acceso_datos/`**: Gestiona la lectura y escritura de los archivos `.json` que actúan como base de datos.
    - **`utils/`**: Proporciona funciones de utilidad, como formateadores de datos que se aplican en el backend.

- **Frontend (JavaScript)**: Es un cliente dinámico que consume la API del backend.
    - **Autónomo**: Cada página carga su propio HTML y luego utiliza JavaScript para buscar todos los datos que necesita de los endpoints `/api/...`.
    - **Renderizado en el cliente**: Todo el renderizado y la manipulación del DOM (actualización de tablas, saldos, gráficos) se realiza en el navegador, creando una experiencia de usuario fluida y rápida sin recargas de página.
    - **Estructura modular en `js/`**:
        - **`pages/`**: Contiene la lógica de inicialización y orquestación para cada página principal (ej. `tradingPage.js`).
        - **`components/`**: Módulos encargados de actualizar partes específicas de la interfaz (ej. `uiUpdater.js`, `tablaCotizacionesUI.js`).
        - **`services/`**: Gestiona la comunicación con la API del backend.

### Flujo desacoplado

1.  El usuario navega a una URL (ej. `/trading`).
2.  Flask sirve un archivo HTML mínimo (`trading.html`) que actúa como un esqueleto.
3.  El archivo JavaScript asociado a esa página (`tradingPage.js`) se ejecuta.
4.  El script de JS realiza llamadas a los endpoints de la API del backend (`/api/cotizaciones`, `/api/historial`, etc.) para obtener los datos en formato JSON.
5.  Una vez recibidos los datos, JavaScript actualiza dinámicamente el DOM para mostrar la información al usuario.

## 🗃️ Estructura del proyecto

```
simulador_exchange/
├── backend/
│   ├── app.py                      # Servidor Flask y punto de entrada
│   ├── config.py                   # Configuración del sistema y constantes globales
│   ├── rutas/                      # Blueprints que definen las vistas y API endpoints
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── trading_vista.py
│   │   ├── billetera_vista.py
│   │   └── api_cotizaciones_vista.py
│   ├── servicios/                  # Lógica de negocio de cada módulo
│   │   ├── api_cotizaciones.py
│   │   ├── estado_billetera.py
│   │   └── velas_logica.py
│   ├── acceso_datos/               # Acceso y manipulación de archivos .json
│   │   ├── datos_billetera.py
│   │   ├── datos_cotizaciones.py
│   │   └── datos_historial.py
│   └── utils/                      # Utilidades auxiliares
│       └── formatters.py
│
├── frontend/
│   ├── templates/                  # Plantillas HTML (contenedores iniciales)
│   │   ├── index.html
│   │   ├── billetera.html
│   │   └── trading.html
│   └── static/                     # Archivos estáticos
│       ├── css/
│       │   ├── styles_index.css
│       │   └── styles_trading.css
│       ├── img/
│       │   └── logo_BlocX.png
│       └── js/                     # Lógica del cliente
│           ├── components/         # Módulos para actualizar la UI
│           ├── pages/              # Scripts de orquestación por página
│           └── services/           # Servicios de comunicación con la API
│
├── datos/                          # Archivos de persistencia
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
