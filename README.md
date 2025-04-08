# Simulador Exchange (Proyecto Educativo)

Este es un proyecto educativo desarrollado para la materia "Algoritmos y Estructuras de Datos I", cuyo objetivo es simular el funcionamiento básico de un exchange de criptomonedas. El sistema permite a los usuarios operar con un saldo ficticio, utilizando datos reales de cotización obtenidos de CoinGecko y Binance.

## 🎯 Objetivos del proyecto

- Familiarizar a los usuarios con el entorno de un exchange cripto.
- Simular compras y ventas con diferentes tipos de órdenes (market, limit, stop-loss).
- Calcular ganancias, pérdidas, y balances del portafolio.
- Almacenar toda la información en archivos locales (.json).
- Aprender cómo se comunican el frontend y backend en una arquitectura moderna (HTML / CSS / Flask / Python).

## ⚙️ Funcionalidades

### Panel general de cotizaciones
- Visualización del top de criptomonedas con:
  - Nombre, ticker, precio, market cap, volumen, supply.
  - Variación en 1h, 24h y 7 días.
- Actualización automática de precios cada 30 segundos.

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
├── backend/               # Código Python del servidor
│   ├── app.py             # Servidor Flask y rutas principales
│   ├── api_cotizaciones.py
│   └── XXXXXXXXXXXXXXXXXXX # FALTA ACTUALIZAR ESTO A MEDIDA QUE VAYAMOS PONIENDO ARCHIVOS
│
├── frontend/
│   ├── templates/         # Archivos HTML (renderizados por Flask)
│   │   ├── index.html
│   │   ├── billetera.html
│   │   └── trading.html
│   └── static/            # Archivos estáticos (CSS/JS)
│       ├── css/estilo.css
│       └── js/funciones.js
│
├── datos/                 # Archivos de persistencia (.json)
│   ├── billetera.json
│   ├── datos_cotizaciones.json
│   ├── datos_velas.json
│   └── historial_operaciones.json
│
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

- Python (3.x)
- Flask
- Requests
- HTML, CSS, JavaScript
- Lightweight Charts (TradingView)

## 📌 Notas

- Todos los datos se almacenan localmente en formato JSON.
- No se requiere conexión a bases de datos externas.
- El sistema está pensado para ser didáctico y extensible.

---

**Grupo 12**  
Fausto Lovera — Patricio Menta — Andrei Veis
