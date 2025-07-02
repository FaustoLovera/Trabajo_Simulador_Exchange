"""Paquete del Subsistema de Trading.

Este paquete encapsula toda la lógica de negocio para la gestión y ejecución
de órdenes de trading en el simulador. Está diseñado con una clara separación
de responsabilidades para manejar la complejidad del ciclo de vida de una orden.

Arquitectura y Componentes Clave:
-   `procesador`: Valida y transforma los datos crudos del formulario de
    operaciones en una estructura de orden estandarizada.
-   `gestor`: Actúa como la interfaz principal para el ciclo de vida de las
    órdenes (crear, cancelar, consultar). Orquesta los otros componentes.
-   `ejecutar_orden`: Contiene la lógica atómica para la ejecución de una
    orden, modificando la billetera y registrando la transacción en el historial.
-   `motor`: Simula un motor de matching de órdenes que verifica continuamente
    las condiciones de mercado para activar órdenes pendientes (Limit, Stop).

Este diseño modular permite mantener, probar y extender las funcionalidades
de trading de manera controlada y robusta.
"""