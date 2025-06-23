# **1. Diagrama de Arquitectura: El Mapa del Sistema**

El siguiente diagrama visualiza la estructura completa de la aplicación, mostrando los componentes principales, sus interacciones y el flujo de información. Los números indican la secuencia de una interacción típica, que se detalla en la sección siguiente.

```
      (1) Pide una página (GET /trading)
+-------------------------------------------------+
|               NAVEGADOR (Usuario)               |
| - Renderiza HTML, CSS y ejecuta JavaScript.     |
| - Envía acciones del usuario (clics, forms).    |
+----------------------+--------------------------+
                       | (14) Muestra UI           ^ (3) Sirve HTML inicial
                       |      actualizada         |
                       v                           |
+----------------------+-------------------------------------------------------------------------------------------+
|                                                   FRONTEND (Cliente)                                             |
|                                         (Se ejecuta completamente en el navegador)                               |
|------------------------------------------------------------------------------------------------------------------|
|  HTML: /templates/*.html                                                                                         |
|  - Esqueleto inicial de la página, carga los scripts JS.                                                         |
|                                                                                                                  |
|  JS: /static/js/                                                                                                 |
|                                                                                                                  |
|  (4) Inicia lógica de página                                   (12) Recibe datos y actualiza la UI               |
|      (DOMContentLoaded)                                              |                                           |
|            +                                                         |                                           |
|            |     +-----------------------------+                     v                                           |
|            +---> |      pages/*.js             | --(11) Llama a componentes--->+--------------------------------+|
|                  | (tradingPage.js, etc)       |                     |        |     components/*.js            | |
|                  | - Orquesta la página.       |                     |        | (uiUpdater, chartRenderer)     | |
|                  | - Llama a servicios.        |                     |        | - Manipulan el DOM.            | |
|                  | - Pasa datos a componentes. |                     |        | - Actualizan tablas, gráficos. | |
|                  +--------------+--------------+                     |        +------------------^-------------+ |
|                                 |                                    |                           | (13)          |
|                                 | (5) Solicita datos a la API        |                           +---------------+
|                                 v                                    |                                           |
|                  +-----------------------------+                     | (10) Devuelve JSON                        |
|                  |    services/apiService.js   |---------------------+-------------------------------------------+
|                  | - Centraliza llamadas fetch().|                                                               |
|                  | - Habla con la API del Backend.|                                                              |
|                  +-----------------------------+                                                                 |
|                                 | (6) Petición HTTP (GET /api/billetera/estado-completo, POST /trading/operar)   |
+---------------------------------v--------------------------------------------------------------------------------+
                                  |
                                  | (2) Sirve HTML para la ruta inicial (GET /trading)
                                  | (7) Recibe petición a la API (GET /api/...)
                                  | (15) Procesa formulario (POST /trading/operar)
+---------------------------------v---------------------------------------------------------------------------------+
|                                                   BACKEND (Servidor)                                              |
|                                            (Aplicación Flask - Python)                                          |
|-----------------------------------------------------------------------------------------------------------------|
| app.py -> __init__.py                                                                                           |
| - Inicia la app Flask y registra las rutas.                                                                     |
|                                                                                                                 |
| +-------------------------------------------------------------------------------------------------------------+ |
| |                                          RUTAS (Capa de Vistas)                                             | |
| | /rutas/*.py (billetera_vista.py, api_externa.py, etc)                                                       | |
| | - Definen los endpoints (URL).                                                                              | |
| | - Reciben peticiones HTTP del Frontend.                                                                     | |
| | - Llaman a la capa de Servicios para obtener/procesar datos.                                                | |
| | - Devuelven JSON (para /api/...) o HTML (para rutas base).                                                  | |
| +-------------------------------------------------------+-----------------------------------------------------+ |
|                                                         | (8, 16) Llama a la lógica de negocio                  |
|                                                         v                                                       |
| +-------------------------------------------------------+-----------------------------------------------------+ |
| |                                        SERVICIOS (Capa de Lógica de Negocio)                                | |
| | /servicios/*.py (trading_logica.py, estado_billetera.py, etc)                                               | |
| | - Contiene el "cerebro" de la app.                                                                          | |
| | - Realiza cálculos (ganancias, swap), formatea datos, procesa operaciones.                                  | |
| | - Orquesta llamadas a la capa de Datos y a APIs externas.                                                   | |
| +---------------------+---------------------------------+-------------------------+---------------------------+ |
|                       | (9, 17) Pide/guarda datos crudos |                         | Llama a API externa       |
|                       v                                  v                         v                           v
| +---------------------+--------------------------------+    +----------------------+---------------------------+
| |        ACCESO A DATOS (Capa de Persistencia)         |    |            APIs EXTERNAS (Fuentes de Datos)     |
| | /acceso_datos/*.py (datos_billetera.py, etc)         |    | - CoinGecko (cotizaciones)                        |
| | - Lee y escribe en los archivos .json.               |    | - Binance (velas)                                 |
| | - Abstrae el manejo de archivos.                     |    |                                                   |
| +----------+------------------+------------------------+    +---------------------------------------------------+
|            |                  |                        |
|            | Lee/Escribe      | Lee/Escribe            | Lee/Escribe
|            v                  v                        v
| +----------+---------+  +-----+--------------+  +------+-------------------+
| |  billetera.json    |  | historial.json     |  | cotizaciones.json        |
| +--------------------+  +--------------------+  +--------------------------+
+-----------------------------------------------------------------------------------------------------------------+
```

## **2. El Flujo de Datos en Acción: Siguiendo los Números**

Este es el recorrido paso a paso de una interacción completa, desde la carga de la página hasta la ejecución de una operación.

#### **A. Flujo de Carga de una Página (Ej: `/trading`)**

1.  **Petición Inicial del Usuario:** El usuario navega a `http://localhost:5000/trading`. El navegador envía una petición `GET` al servidor.

2.  **El Backend Sirve el "Contenedor" HTML:** El servidor Flask recibe la petición. La capa de **Rutas** (`rutas/trading_vista.py`) la asocia con la función `mostrar_trading_page()` y devuelve el archivo `trading.html`. Este HTML es solo un esqueleto, no contiene datos dinámicos.

3.  **El Navegador se Prepara:** El navegador recibe este HTML, lo analiza y comienza a cargar los recursos vinculados, como los archivos CSS y los scripts de JavaScript.

4.  **El Frontend Despierta:** Una vez que la estructura básica del HTML está lista (`DOMContentLoaded`), el navegador ejecuta `tradingPage.js`. Aquí arranca toda la lógica del lado del cliente.

5.  **El Frontend Solicita Datos:** `tradingPage.js` (la capa `pages`) actúa como el "director" de la página. Sabe que necesita datos (cotizaciones, estado de billetera, etc.) para funcionar. Para obtenerlos, llama a las funciones del módulo `services/apiService.js`.

6.  **Peticiones a la API del Backend:** `apiService.js` convierte esas llamadas en peticiones HTTP reales. Por ejemplo, realiza una petición `GET` a la URL `/api/billetera/estado-completo`. La clave aquí es el prefijo `/api/`, que el backend identifica como una solicitud de datos, no de una página completa.

7.  **La API del Backend Recibe la Solicitud:** Flask recibe esta nueva petición. La capa de **Rutas** la identifica como una llamada a la API y entiende que debe devolver datos, no HTML.

8.  **Delegación a la Lógica de Negocio (Servicios):** La función de la ruta (ej: `get_estado_billetera_completo()`) no realiza los cálculos. Delega esa responsabilidad llamando a la función correspondiente en la capa de **Servicios** (ej: `estado_actual_completo()`).

9.  **Los Servicios Orquestan la Respuesta:** La función del servicio es el cerebro. Llama a la capa de **Acceso a Datos** para leer la información cruda de los archivos `.json`, realiza los cálculos necesarios (ganancias, totales), formatea los datos y los empaqueta.

10. **El Backend Serializa y Devuelve Datos JSON:** El servicio devuelve el paquete de datos a la ruta. La ruta utiliza la función `jsonify` de Flask para convertir la estructura de datos de Python en una cadena de texto en formato **JSON**, que es enviada como respuesta al navegador.

11. **El Frontend Recibe y Procesa el JSON:** De vuelta en el navegador, la promesa `fetch` en `apiService.js` se resuelve, entregando los datos JSON. `JSON.parse()` (a menudo manejado automáticamente por `fetch`) convierte esta cadena de texto de nuevo en un objeto JavaScript utilizable.

12. **El Director Distribuye los Datos:** `tradingPage.js` recibe los objetos de datos y sabe qué componente de la UI necesita qué información.

13. **Los Especialistas de la UI entran en Acción:** El director pasa los datos a los módulos `components`. Por ejemplo, entrega los datos del historial a `UIUpdater.js` y los datos de velas a `chartRenderer.js`.

14. **Renderizado del Lado del Cliente:** Estos componentes manipulan el DOM. `UIUpdater` crea dinámicamente las filas `<tr>` para la tabla del historial, y `chartRenderer` dibuja el gráfico. El usuario ve cómo la página "vacía" cobra vida sin necesidad de recargarla. Este proceso se llama **Renderizado del Lado del Cliente (Client-Side Rendering)**.

#### **B. Flujo de una Operación (Ej: Comprar BTC)**

15. **El Usuario Envía el Formulario:** El usuario llena el formulario y hace clic en "CONFIRMAR". El navegador empaqueta los datos y envía una petición `POST` a `/trading/operar`.

16. **La Ruta del Backend Procesa la Acción:** El backend recibe el `POST`. La ruta `procesar_trading_form()` extrae los datos y llama a la función principal de la capa de **Servicios**: `procesar_operacion_trading()`.

17. **El Servicio Ejecuta el Cambio de Estado:** Aquí ocurren los cambios permanentes. `procesar_operacion_trading()` realiza la validación crítica (saldo, montos válidos), calcula los resultados del swap y, si todo es correcto, llama a la capa de **Acceso a Datos** para que **modifique** los archivos `billetera.json` y `historial.json`. Finalmente, devuelve un mensaje de éxito o error.

## **3. Glosario Técnico y Piezas del Sistema**

#### **I. Conceptos de Arquitectura y Diseño**

*   **Arquitectura de Software:** Es el diseño fundamental de un sistema. Define los componentes principales, sus responsabilidades y cómo interactúan entre sí. Una buena arquitectura hace que el sistema sea más fácil de entender, mantener y ampliar.
*   **Arquitectura Desacoplada (Decoupled Architecture):** Un principio de diseño donde los componentes (frontend y backend) son independientes y se comunican a través de una interfaz bien definida (la API). El gran beneficio es que se puede cambiar o incluso reemplazar un componente (ej. crear una app móvil que consuma el mismo backend) sin afectar al otro.
*   **Capa (Layer):** Una forma de organizar el código en grupos lógicos con responsabilidades específicas. En este proyecto, el backend se divide en capas (Rutas, Servicios, Acceso a Datos), lo que promueve el principio de **Separación de Intereses (Separation of Concerns)** y hace que el código sea más limpio.

#### **II. Comunicación y Datos (Cliente-Servidor)**

*   **API (Application Programming Interface):** Un contrato que define cómo dos piezas de software deben comunicarse. Establece un conjunto de reglas, endpoints y formatos de datos que el servidor expone para que los clientes puedan interactuar con él de manera predecible.
*   **API REST (Representational State Transfer):** Un estilo arquitectónico para diseñar APIs que se basa en principios como:
    1.  **Operaciones sobre Recursos:** La API se centra en "recursos" (ej: `cotizaciones`, `billetera`).
    2.  **Uso de Métodos HTTP:** Se utilizan los verbos estándar (`GET` para obtener, `POST` para crear) para manipular estos recursos.
    3.  **Comunicación sin Estado (Stateless):** Cada petición del cliente debe contener toda la información necesaria para ser entendida. El servidor no guarda ningún contexto del cliente entre peticiones.
*   **Endpoint:** Una URL específica en la API que expone un recurso o una acción. Por ejemplo, `/api/cotizaciones` y `/api/historial` son dos endpoints distintos.
*   **JSON (JavaScript Object Notation):** Un formato de texto ligero para el intercambio de datos. Es el "idioma" que hablan el frontend y el backend. Su estructura es fácilmente convertible a objetos de JavaScript, lo que lo hace ideal para aplicaciones web.

#### **III. Componentes y Tecnologías del Backend (Python/Flask)**

*   **Backend:** La parte de la aplicación que se ejecuta en el servidor. Es responsable de la lógica de negocio, la seguridad y la gestión de datos.
*   **Flask:** Un micro-framework de Python para construir aplicaciones web. Proporciona las herramientas esenciales para manejar rutas y peticiones HTTP, permitiendo una gran flexibilidad en la estructura del proyecto.
*   **Patrón de Fábrica de Aplicaciones (Application Factory):** La práctica de crear la instancia de la aplicación Flask dentro de una función (`crear_app()`) en lugar de globalmente. Esto facilita las pruebas y la configuración de múltiples instancias.
*   **Blueprint:** Un componente de Flask para organizar las rutas en grupos modulares. Permite que la aplicación sea más escalable y que las rutas relacionadas con una funcionalidad (ej. `trading`) estén juntas en un mismo archivo.
*   **Persistencia:** La capacidad de que los datos se conserven incluso después de que el programa se cierre. En este proyecto, se logra mediante la escritura de datos en archivos `.json` en el disco duro.
*   **`Decimal` (Tipo de Dato):** Un tipo numérico de alta precisión utilizado para cálculos financieros. A diferencia de los números de punto flotante estándar, `Decimal` evita pequeños errores de redondeo que son inaceptables al manejar dinero.

#### **IV. Componentes y Tecnologías del Frontend (JavaScript)**

*   **Frontend:** La parte de la aplicación que se ejecuta en el navegador del usuario y con la que este interactúa directamente.
*   **DOM (Document Object Model):** Una representación en memoria de la estructura de un documento HTML. JavaScript utiliza el DOM para leer y modificar dinámicamente el contenido y la apariencia de la página.
*   **Manipulación del DOM:** El proceso de usar JavaScript para cambiar el DOM, lo que resulta en actualizaciones visuales en la página sin necesidad de recargarla. Esta es la base del renderizado del lado del cliente.
*   **Manejo de Eventos (Event Handling):** La capacidad de JavaScript para responder a acciones del usuario (un `click` en un botón, un `change` en un selector). Un "escuchador de eventos" (`event listener`) espera a que ocurra un evento y ejecuta una función en respuesta.
*   **Código Asíncrono (`async`/`await`):** En JavaScript, las operaciones de red (como las peticiones `fetch` a la API) son asíncronas. Esto significa que el código no espera a que la operación termine, sino que continúa ejecutándose. `async/await` es una sintaxis moderna que permite escribir código asíncrono de una manera que parece síncrona, haciéndolo mucho más fácil de leer y depurar.

## **4. Las Piezas del Engranaje: Descripción Detallada de Capas**

*   **Capa de Presentación (Frontend):**
    *   **Propósito:** Crear la experiencia visual e interactiva del usuario. Es autónoma y solo necesita conocer el "contrato" de la API del backend para funcionar.
    *   **Componentes Clave:**
        *   **`pages/*.js`:** Los orquestadores de cada página. Inician la carga de datos y coordinan la actualización de la UI.
        *   **`services/apiService.js`:** El punto único de comunicación con el backend. Centraliza toda la lógica de `fetch`.
        *   **`components/*.js`:** Módulos reutilizables con responsabilidades únicas (renderizar el gráfico, actualizar la tabla, etc.).

*   **Capa de Vistas/Rutas (Backend - `rutas/`):**
    *   **Propósito:** Actuar como el controlador de tráfico del backend. Es la puerta de entrada para todas las peticiones HTTP.
    *   **Funcionamiento:** Asocia las URLs (endpoints) con funciones de Python. No contiene lógica de negocio; su trabajo es validar la petición (si es necesario) y delegar la tarea a la capa de servicios.

*   **Capa de Lógica de Negocio (Backend - `servicios/`):**
    *   **Propósito:** Es el cerebro de la aplicación. Aquí residen todas las reglas, cálculos y procesos de negocio.
    *   **Funcionamiento:** Orquesta las operaciones complejas. Por ejemplo, para un `swap`, obtiene precios, valida el saldo, calcula las cantidades, invoca a la capa de datos para guardar los cambios y prepara una respuesta.

*   **Capa de Acceso a Datos (Backend - `acceso_datos/`):**
    *   **Propósito:** Abstraer y gestionar la interacción con la fuente de datos (en este caso, los archivos `.json`).
    *   **Funcionamiento:** Proporciona funciones simples y claras como `cargar_billetera()` o `guardar_en_historial()`. La capa de servicios no necesita saber cómo o dónde se guardan los datos, solo pide que se realicen las operaciones.