### **Diagrama de Arquitectura: "BlocX - Simulador de Exchange"**

```
+-----------------------------------------------------------------------------------------------------------------------+
|                                                  NAVEGADOR DEL USUARIO                                                |
|      - Renderiza HTML/CSS, ejecuta JS.                                                                                |
|      - Envía acciones del usuario (clics, formularios) al Backend.                                                    |
|      - Muestra notificaciones de SweetAlert2.                                                                         |
+------------------------------------------+--------------------------------------------------+-------------------------+
                                           |                                                  |                         ^
 (1) Petición inicial (GET /trading)       | (16) Muestra UI actualizada                      | (3) Sirve HTML inicial  |
                                           |      con datos de la API                         | (desde layout.html)     |
                                           v                                                  |                         |
+------------------------------------------+--------------------------------------------------+-------------------------+
|                                                      FRONTEND (Cliente)                                               |
|                                            (Se ejecuta completamente en el navegador)                                   |
|-----------------------------------------------------------------------------------------------------------------------|
| HTML: /templates/                                                                                                     |
|  - layout.html: Plantilla base con NAV, scripts comunes.                                                              |
|  - trading.html, billetera.html: Heredan de layout.html y definen el contenido específico de la página.               |
|  - _flashes.html: Template parcial para manejar los mensajes del backend con SweetAlert2.                             |
|                                                                                                                       |
| JS: /static/js/                                                                                                       |
|                                                                                                                       |
|  (4) Inicia lógica de página           (14) Recibe JSON, actualiza UI        (18) Muestra Toast/Popup                  |
|      (DOMContentLoaded)                         |                                     ^                               |
|            +                                    |                                     |                               |
|            |     +----------------------------+ v                                     |                               |
|            +---> |   pages/tradingPage.js     | --(15) Llama a componentes--->+---------------------------------+    |
|                  |   - Orquesta la página.    |                               |    components/*.js              |    |
|                  |   - Llama a servicios.     |                               |    (chartRenderer, uiUpdater)   |    |
|                  |   - Gestiona eventos.      |                               |    - Manipulan el DOM.          |    |
|                  +------------+---------------+                               +------------------^--------------+    |
|                               |                                                                  | (15)             |
|                               | (5, 17) Solicita datos a API                                     +------------------+
|                               v                                                                                     |
|                  +----------------------------+  (13) Devuelve JSON          +------------------------------------+  |
|                  |  services/apiService.js    | <--------------------------+ | services/sweetalert-config.js      |  |
|                  |  - Centraliza llamadas     |                              | - Configura SweetAlert2.           |  |
|                  |    fetch() al backend.     |                              | - Procesa mensajes de _flashes.html|  |
|                  +----------------------------+                              +------------------------------------+  |
|                               | (6) Petición HTTP (GET /api/..., POST /trading/operar, POST /api/orden/cancelar/...) |
+-------------------------------v-------------------------------------------------------------------------------------+
                                |                                                                                       (2) Sirve HTML
                                | (7) Recibe petición a la API (GET /api/billetera/estado-completo)                     (vía render_template)
                                | (A) Recibe formulario (POST /trading/operar)
                                | (C) Recibe cancelación (POST /api/orden/cancelar/...)
+-------------------------------v-------------------------------------------------------------------------------------+
|                                                       BACKEND (Servidor)                                            |
|                                                 (Aplicación Flask - Python)                                         |
|---------------------------------------------------------------------------------------------------------------------|
| app.py -> __init__.py                                                                                               |
| - Inicia la app Flask y registra las rutas desde /rutas.                                                            |
|                                                                                                                     |
| +-----------------------------------------------------------------------------------------------------------------+ |
| |                                            RUTAS (Capa de Vistas)                                               | |
| | /rutas/*.py (billetera_vista.py, api_externa.py, trading_vista.py)                                              | |
| | - Definen los endpoints (URL).                                                                                  | |
| | - (8, B, D) Delegan la lógica de negocio a la capa de Servicios.                                                | |
| | - Devuelven JSON (para /api/...) o HTML (para rutas base).                                                      | |
| +-----------------------------------------------------------+-----------------------------------------------------+ |
|                                                             | (9) Llama a la lógica de negocio                      |
|                                                             v                                                       |
| +-----------------------------------------------------------+-----------------------------------------------------+ |
| |                                     SERVICIOS (Capa de Lógica de Negocio)                                       | |
| | /servicios/*.py (trading_logica.py, estado_billetera.py, api_cotizaciones.py)                                   | |
| | - trading_logica.py: procesar_operacion_trading(), verificar_y_ejecutar_ordenes_pendientes(), cancelar...()     | |
| | - estado_billetera.py: estado_actual_completo()                                                                 | |
| | - api_cotizaciones.py: obtener_datos_criptos_coingecko()                                                        | |
| +-------------------------+-----------------------------------+--------------------+------------------------------+ |
|                           | (10) Pide/guarda datos crudos      |                    | (F) Llama a API externa      |
|                           v                                   v                    v                              v
| +-------------------------+-------------------------------+  +---------------------+----------------------------+
| |        ACCESO A DATOS (Capa de Persistencia)          |  |            APIs EXTERNAS (Fuentes de Datos)    |
| | /acceso_datos/*.py (datos_billetera.py, etc)          |  | - CoinGecko (cotizaciones)                       |
| | - Lee y escribe en los archivos .json.                |  | - Binance (velas)                                |
| | - Abstrae el manejo de archivos.                      |  |                                                  |
| +----------+------------------+-------------------------+  +--------------------------------------------------+
|            |                  |                         |
|            | (11) Lee/Escribe | (E) Lee/Escribe         | (G) Lee/Escribe
|            v                  v                         v
| +----------+---------+  +-----+--------------+  +-------+------------------+  +--------------------------+
| |  billetera.json    |  | historial.json     |  | ordenes_pendientes.json  |  | cotizaciones.json        |
| +--------------------+  +--------------------+  +--------------------------+  +--------------------------+
+---------------------------------------------------------------------------------------------------------------------+

```

### **El Flujo de Datos en Acción: Siguiendo los Números y Letras**

Aquí se detallan los flujos de trabajo más importantes de tu aplicación.

#### **A. Flujo de Carga de una Página (Ej: `/trading`)**

*Este flujo muestra cómo una página se carga y se llena de datos dinámicamente.*

1.  **Petición Inicial:** El usuario navega a `http://.../trading`. El navegador envía una petición `GET` al servidor Flask.
2.  **Servir el "Contenedor":** La capa de **Rutas** (`trading_vista.py`) recibe la petición. Llama a `render_template('trading.html')`.
3.  **Herencia de Plantillas:** `trading.html` hereda de `layout.html`, que contiene la estructura principal, la barra de navegación y los scripts comunes. Flask une todo y lo envía como una única respuesta HTML.
4.  **El Frontend Despierta:** El navegador recibe el HTML y ejecuta los scripts, incluyendo `tradingPage.js`.
5.  **Solicitud de Datos:** `tradingPage.js` (en su función `initialize`) se da cuenta de que necesita datos (estado de billetera, historial, etc.) y llama a las funciones correspondientes en `apiService.js`.
6.  **Llamada a la API del Backend:** `apiService.js` realiza múltiples peticiones `fetch` a los endpoints de la API del backend, como `GET /api/billetera/estado-completo` y `GET /api/ordenes-abiertas`.
7.  **Rutas de API Responden:** La capa de **Rutas** del backend (`billetera_vista.py`) recibe estas peticiones de API.
8.  **Delegación a Servicios:** La ruta no hace el trabajo; llama a la función apropiada en la capa de **Servicios** (ej. `estado_actual_completo()`).
9.  **Orquestación en Servicios:** El servicio es el "cerebro". Llama a la capa de **Acceso a Datos** para obtener la información cruda.
10. **Acceso a Datos:** Módulos como `datos_billetera.py` leen la información de los archivos `.json`.
11. **Retorno de Datos Crudos:** Los datos leídos de los `.json` se devuelven a la capa de servicios.
12. **Procesamiento y Formato:** El servicio procesa los datos (calcula P&L, formatea números) y los devuelve a la ruta.
13. **Respuesta JSON:** La ruta toma los datos procesados, los convierte a formato JSON con `jsonify()` y los envía como respuesta al navegador.
14. **El Frontend Recibe:** La promesa `fetch` en `apiService.js` se resuelve, entregando los datos como un objeto JavaScript.
15. **Renderizado en el Cliente:** `tradingPage.js` recibe los datos y los pasa a componentes especializados como `UIUpdater.js` o `chartRenderer.js`, que manipulan el DOM para construir las tablas y el gráfico dinámicamente.
16. **UI Actualizada:** El usuario ve la página cobrar vida con toda la información.

#### **B. Flujo de Creación de una Orden Límite**

*Este flujo explica qué sucede cuando el usuario envía el formulario de trading.*

A. **Envío del Formulario:** El usuario rellena el formulario (cantidad, precio límite) y hace clic en "CONFIRMAR". El navegador envía una petición `POST` a `/trading/operar`.
B. **Delegación a Servicios:** La ruta `procesar_trading_form()` en `trading_vista.py` recibe el formulario y llama a la función `procesar_operacion_trading()` en la capa de **Servicios**.
C. **Despacho de Órdenes:** `procesar_operacion_trading()` detecta que `tipo_orden` es "limit". En lugar de ejecutarla, llama a la función interna `_crear_orden_pendiente()`.
D. **Reserva de Fondos y Creación:** `_crear_orden_pendiente()` hace dos cosas cruciales:
    1. Llama a la capa de **Acceso a Datos** para modificar `billetera.json`, moviendo los fondos de "disponible" a "reservado".
    2. Crea el objeto de la nueva orden.
E. **Persistencia de la Orden:** Llama a `agregar_orden_pendiente()` en `datos_ordenes.py` para guardar la nueva orden en `ordenes_pendientes.json`.
F. **Notificación de Éxito:** La función devuelve un mensaje de éxito. La ruta de Flask lo captura con `flash()`. El navegador es redirigido a la misma página.
G. **Popup de SweetAlert:** En la nueva carga de la página, el template `_flashes.html` detecta el mensaje "flasheado" y el script `sweetalert-config.js` lo muestra como una notificación Toast.

#### **C. Flujo del Motor de Ejecución de Órdenes**

*Este flujo es asíncrono y se dispara periódicamente.*

1. **Disparo Periódico:** El `indexPage.js` o un futuro mecanismo en `tradingPage.js` llama a `GET /api/actualizar` cada 15 segundos.
2. **Actualización de Cotizaciones:** La ruta `actualizar()` en `api_externa.py` primero llama a `obtener_datos_criptos_coingecko()` para refrescar las cotizaciones en `cotizaciones.json` y en el caché de memoria.
3. **¡Motor en Marcha!:** Inmediatamente después, la misma ruta llama a `verificar_y_ejecutar_ordenes_pendientes()` del servicio de trading.
4. **Verificación:** La función carga todas las órdenes "pendientes" y, para cada una, obtiene el precio actual del caché. Compara el precio actual con el `precio_disparo` de la orden.
5. **Ejecución:** Si la condición se cumple, llama a `_ejecutar_orden_pendiente()`. Esta función:
    - Libera los fondos reservados.
    - Calcula la comisión.
    - Acredita el nuevo saldo.
    - Guarda la transacción en `historial.json`.
    - Cambia el estado de la orden a "ejecutada".
    - Guarda los cambios en `billetera.json` y `ordenes_pendientes.json`.

### **Glosario de Componentes y Responsabilidades**

*   **Backend (`/backend`)**: El cerebro y la sala de máquinas. Gestiona toda la lógica, los datos y la seguridad. Expone su funcionalidad a través de una API.
    *   **Rutas (`/rutas`)**: Los "controladores de tráfico". Reciben peticiones HTTP, delegan el trabajo a los servicios y devuelven la respuesta final (HTML o JSON).
    *   **Servicios (`/servicios`)**: El "núcleo del negocio". Contiene toda la lógica de cálculo, procesamiento de órdenes, formato de datos y orquestación entre diferentes fuentes de datos.
    *   **Acceso a Datos (`/acceso_datos`)**: Los "bibliotecarios". Saben exactamente cómo leer y escribir en los archivos `.json`, manteniendo este detalle oculto del resto de la aplicación.

*   **Frontend (`/frontend`)**: La cara visible de la aplicación. Es un cliente que se ejecuta en el navegador del usuario.
    *   **Templates (`/templates`)**: Esqueletos HTML. `layout.html` proporciona la estructura común, y las otras plantillas la extienden. `_flashes.html` es un "componente" de plantilla reutilizable.
    *   **JS - Pages (`/js/pages`)**: Los "directores de orquesta" de cada página. Inician la carga de datos y coordinan todas las acciones de la interfaz.
    *   **JS - Services (`/js/services`)**: Módulos de soporte. `apiService.js` es el "embajador" que habla con la API del backend. `sweetalert-config.js` gestiona las notificaciones.
    *   **JS - Components (`/js/components`)**: Módulos "especialistas". Cada uno se enfoca en una tarea específica de la UI, como actualizar tablas (`uiUpdater.js`) o dibujar el gráfico (`chartRenderer.js`).

*   **Persistencia (`/datos/*.json`)**: La "base de datos" del proyecto. Archivos de texto plano que almacenan el estado de la aplicación (billetera, historial, órdenes) y permiten que los datos sobrevivan entre sesiones.