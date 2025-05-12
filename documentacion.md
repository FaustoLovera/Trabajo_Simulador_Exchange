**TPO_simulador_exchange** es un simulador de exchange de criptomonedas desarrollado en Python y Flask, orientado a prácticas académicas. Permite consultar cotizaciones en tiempo real, realizar operaciones de compra/venta simuladas y visualizar el estado de la billetera del usuario.

---

## 📦 Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/FaustoLovera/Trabajo_Simulador_Exchange.git
cd TPO_simulador_exchange
```

2. Crear entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```bash
python -m backend.app
```

---

## 🗂️ Estructura principal del backend

```
backend/
├── app.py                  # Punto de entrada principal de la app
├── __init__.py             # Configuración de Flask, Swagger y registros
├── rutas/                  # Blueprints y vistas del sistema
│   ├── __init__.py         # Inicialización de blueprints
│   ├── home.py             # Ruta principal
│   ├── trading_vista.py    # Interfaz de compra/venta
│   ├── billetera_vista.py  # Vista para la billetera
│   └── api_externa.py      # Rutas para datos externos
├── servicios/              # Lógica de negocio: consultas API, cálculo, etc.
│   ├── api_cotizaciones.py # Consulta cotizaciones a CoinGecko
│   ├── trading_logica.py   # Lógica principal de operaciones de trading
│   ├── velas_logica.py     # Consulta y guarda datos de velas de Binance
│   ├── cotizaciones.py     # Procesa y ordena cotizaciones
│   └── estado_billetera.py # Cálculo de estadísticas y visualización de billetera
├── acceso_datos/           # Lectura y escritura de archivos JSON
│   ├── datos_billetera.py
│   ├── datos_historial.py
│   └── datos_cotizaciones.py
frontend/
├── templates/              # Plantillas HTML (Jinja2)
├── static/                 # CSS, JS e imágenes estáticas
```

---

## 🚀 Funcionalidad básica

1. **Ver cotizaciones**: Se consultan desde la API de CoinGecko.
2. **Operar**: Se simula la compra o venta de criptomonedas.
3. **Billetera**: Se visualiza el balance actual y el historial de operaciones.

---

## 🔧 Configuración

El archivo `config.py` centraliza:

- Las rutas a archivos JSON (`datos/`)
- Clave secreta de Flask
- URLs de APIs externas (CoinGecko y Binance)
- Parámetros de scraping
- Configuración global de `Decimal`

---

## 📌 Notas

- El proyecto está diseñado para ejecutarse en **entorno local**.
- A futuro se planea incorporar tests automáticos.
- La documentación Swagger está disponible en `http://localhost:5000/apidocs`.

---

# 🧩 Descripción de módulos clave

### `backend/app.py`

Punto de entrada principal de la aplicación.

- Crea la instancia Flask mediante `crear_app()` (importado desde `__init__.py`).
- Configura Swagger para la documentación interactiva.
- Ejecuta el servidor solo si el archivo se ejecuta directamente (bloque `if __name__ == "__main__"`).

---

### `backend/__init__.py`

- Define la función `crear_app()` que:
  - Crea la app Flask.
  - Registra los blueprints desde `backend.rutas`.
  - Configura la clave secreta desde `config.py`.

---

### `backend/rutas/home.py`

- Define un blueprint `bp` que maneja la ruta principal (`/`).
- Puede incluir lógicas complementarias al `index`.

---

### `backend/rutas/trading_vista.py`

- Define un blueprint `bp` para las rutas de compra y venta.
- Utiliza lógica de `trading_logica.py` y lectura de archivos desde `acceso_datos/`.
- Encargado de procesar operaciones y mostrar la billetera.

---

### `backend/servicios/api_cotizaciones.py`

- Contiene funciones para obtener cotizaciones de criptomonedas desde la API de CoinGecko.
- Incluye funciones auxiliares para ordenar o filtrar datos antes de usarlos en la app.

---

### `backend/servicios/trading_logica.py`

- Lógica principal de las operaciones de trading:
  - Cálculo de compra/venta.
  - Verificación de saldos.
  - Cálculo de precio promedio y ganancias/perdidas.

---

### `backend/servicios/velas_logica.py`

- Obtiene y guarda datos de velas (candlestick) desde la API de Binance.
- Sirve como base para análisis técnico o visualización de gráficos (a futuro).

---

### `backend/acceso_datos/datos_billetera.py`

- Lectura y escritura de la billetera en `datos/billetera.json`.
- Gestiona saldos de criptomonedas y USDT.

---

### `backend/acceso_datos/datos_historial.py`

- Maneja el historial de operaciones guardado en `datos/historial.json`.
- Permite consultar o registrar movimientos.

---

### `config.py`

- Define rutas absolutas a los archivos del sistema (`cotizaciones.json`, `billetera.json`, etc.).
- Contiene claves, parámetros, URLs de API y configuración global de decimales.

---

### `backend/rutas/billetera_vista.py`

- Muestra y actualiza visualmente el estado de la billetera.
- Utiliza fragmentos HTML renderizados desde el backend.

---

### `backend/rutas/api_externa.py`

- Expone rutas de la API que devuelven datos en formato JSON (probablemente para frontend dinámico o AJAX).

---

### `backend/servicios/cotizaciones.py`

- Procesamiento y filtrado adicional de cotizaciones antes de ser mostradas.

---

### `backend/servicios/estado_billetera.py`

- Cálculo de estadísticas y visualización del estado general de la billetera.

---

### `backend/utils/formateo_decimales.py`

- Centraliza el formateo consistente de decimales para mostrar precios y saldos en la interfaz.

---

### `backend/swagger.yaml`

- Archivo de definición OpenAPI (YAML) para Swagger. Describe rutas, parámetros y respuestas esperadas.


---

# Inicio Proyecto

## app.py

## Explicación paso a paso de `app.py`

Este archivo es el punto de entrada del proyecto. Se encarga de crear la app de Flask, activar Swagger para documentación y definir una ruta principal.

---

### 1. Importaciones

```python
from flask import render_template
```
Importa la función `render_template` que permite mostrar archivos HTML en el navegador.

```python
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
```
Importa una función que consulta precios de criptomonedas desde CoinGecko.

```python
from . import crear_app
```
Importa la función `crear_app()` que configura y devuelve la app Flask. Está definida en `__init__.py`.

```python
from flasgger import Swagger
```
Importa `Swagger`, una herramienta que genera documentación interactiva para la API.

---

### 2. Creación de la app y Swagger

```python
app = crear_app()
```
Llama a `crear_app()` y devuelve una instancia de Flask ya configurada.

```python
swagger = Swagger(app)
```
Activa Swagger sobre la app. La documentación estará disponible en `http://localhost:5000/apidocs`.

---

> Nota: anteriormente esta ruta estaba definida directamente en `app.py`, pero ahora forma parte del blueprint `home` definido en `rutas/home.py`.


### 4. Arranque del servidor

```python
if __name__ == "__main__":
    app.run(debug=True)
```

Este bloque significa: "si este archivo se ejecuta directamente, levantá el servidor Flask en modo debug".

---

### 5. ¿Por qué se separan `app.py` y `__init__.py`?

Esta separación sigue el patrón recomendado por Flask conocido como *Application Factory Pattern*.

#### Ventajas:

- **Modularidad**: `__init__.py` se encarga de crear y configurar la app. `app.py` solo la ejecuta.
- **Reutilización**: Podés importar `crear_app()` en otros contextos (por ejemplo, para testing) sin lanzar el servidor.
- **Escalabilidad**: Permite crear múltiples instancias de la aplicación con diferentes configuraciones si fuera necesario.
- **Separación de responsabilidades**: `__init__.py` configura la app, `app.py` se encarga del arranque.

#### Resumen:

| Archivo        | Rol                                                       |
|----------------|------------------------------------------------------------|
| `__init__.py`  | Configura y devuelve la instancia de Flask (`crear_app`)   |
| `app.py`       | Ejecuta la aplicación (`app.run(debug=True)`)              |

---

## Explicación paso a paso de `__init__.py`

Este archivo contiene la función `crear_app()`, que se encarga de crear y configurar la instancia de Flask. Esta función devuelve una aplicación completamente configurada y lista para ser ejecutada por `app.py`.

---

### 1. Importaciones

```python
from flask import Flask
from config import FLASK_SECRET_KEY
from backend.utils.formateo_decimales import registrar_filtros
from backend.rutas import registrar_rutas
```

Estas líneas importan:

- `Flask`: clase principal para crear una app Flask.
- `FLASK_SECRET_KEY`: clave secreta usada para sesiones y seguridad, definida en `config.py`.
- `registrar_filtros`: función auxiliar que registra filtros personalizados para templates.
- `registrar_rutas`: función que registra todas las rutas del sistema (blueprints).

---

### 2. Creación de la app Flask

```python
app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)
```

Se crea una instancia de Flask, indicando:

- `__name__`: ayuda a Flask a saber dónde están los archivos.
- `static_folder`: ruta a los archivos CSS, JS e imágenes.
- `template_folder`: ruta a los archivos HTML (Jinja2).

---

### 3. Configuración de clave secreta

```python
app.secret_key = FLASK_SECRET_KEY
```

Configura la clave secreta que permite usar sesiones y mostrar mensajes "flash" en Flask.

---

### 4. Registro de componentes

```python
registrar_filtros(app)
registrar_rutas(app)
```

- `registrar_filtros`: agrega filtros personalizados de formateo de decimales que luego se pueden usar en templates HTML.
- `registrar_rutas`: importa y registra todas las rutas del sistema (por ejemplo, `/`, `/billetera`, `/trading`).

---

### 5. Devolver la app

```python
return app
```

Una vez configurada, se devuelve la instancia `app` para que pueda ser utilizada por `app.py`.