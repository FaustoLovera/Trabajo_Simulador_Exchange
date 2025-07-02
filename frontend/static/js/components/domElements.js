/**
 * @file Componente que centraliza las referencias a los elementos del DOM.
 * @module DOMElements
 * @description Este módulo exporta un único objeto `DOMElements` que contiene referencias
 * cacheadas a los elementos del DOM utilizados con frecuencia en la aplicación.
 * Este enfoque mejora el rendimiento al evitar consultas repetitivas al DOM y
 * facilita el mantenimiento al tener todos los selectores en un solo lugar.
 */

/**
 * Almacena referencias cacheadas de jQuery a los elementos del DOM de la interfaz.
 * @namespace DOMElements
 * @type {Object<string, JQuery>}
 */
export const DOMElements = {
    /** @type {JQuery} El formulario principal de operaciones de trading. */
    form: $('#formulario-trading'),

    /** @type {JQuery} El selector principal para elegir la criptomoneda (ej. BTC, ETH). */
    selectorPrincipal: $('#cripto'),

    /** @type {JQuery} El menú desplegable para seleccionar la moneda de pago en una compra. */
    selectorPagarCon: $('#moneda-pago'),

    /** @type {JQuery} El menú desplegable para seleccionar la moneda a recibir en una venta. */
    selectorRecibirEn: $('#moneda-recibir'),

    /** @type {JQuery} El botón de acción para iniciar una operación de 'Comprar'. */
    botonComprar: $('.boton-comprar'),

    /** @type {JQuery} El botón de acción para iniciar una operación de 'Vender'. */
    botonVender: $('.boton-vender'),

    /** @type {JQuery} El botón final para confirmar y enviar la transacción. */
    botonConfirmar: $('.boton-confirmar'),

    /** @type {JQuery} El campo de entrada oculto que almacena la acción actual ('compra' o 'venta'). */
    inputAccion: $('#accion'),

    /** @type {JQuery} El contenedor del campo 'Pagar con'. */
    campoPagarCon: $('#campo-pagar-con'),

    /** @type {JQuery} El contenedor del campo 'Recibir en'. */
    campoRecibirEn: $('#campo-recibir-en'),

    /** @type {JQuery} El elemento `<span>` que muestra el saldo disponible del usuario. */
    spanSaldoDisponible: $('#saldo-disponible'),

    /** @type {JQuery} Los botones de radio para cambiar el modo de ingreso ('monto' vs 'total'). */
    radioModoIngreso: $('input[name="modo-ingreso"]'),

    /** @type {JQuery} La etiqueta para el botón de radio 'Cantidad (Cripto)'. */
    labelModoMonto: $('#label-modo-monto'),

    /** @type {JQuery} La etiqueta para el campo de entrada de monto/total. */
    labelMonto: $('label[for="monto"]'),

    /** @type {JQuery} El campo de entrada principal para el monto o total. */
    inputMonto: $('#monto'),

    /** @type {JQuery} La etiqueta para el botón de radio 'Total (USDT)'. */
    labelModoTotal: $('#label-modo-total'),
};
