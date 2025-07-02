"""Paquete de Servicios (Lógica de Negocio).

Este paquete encapsula la lógica de negocio principal de la aplicación, actuando
como un intermediario entre la capa de rutas (controladores) y la capa de
acceso a datos.

Responsabilidades clave:
-   Orquestar operaciones que involucran múltiples fuentes de datos.
-   Realizar cálculos complejos (ej. valoración de portafolio, ejecución de trades).
-   Interactuar con APIs externas para obtener datos en tiempo real.
-   Implementar las reglas de negocio y flujos de trabajo del simulador.

Esta separación de responsabilidades promueve un código más limpio, modular
y fácil de probar y mantener.
"""