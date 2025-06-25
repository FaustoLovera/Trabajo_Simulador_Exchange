/**
 * @module DOMElements
 * @description Centraliza las referencias a los elementos del DOM a los que se accede con frecuencia.
 * Este patrón mejora el rendimiento al cachear los objetos jQuery, evitando consultas
 * redundantes al DOM y facilitando el mantenimiento del código.
 */

/**
 * Un objeto que contiene referencias cacheadas de jQuery a los elementos del DOM
 * utilizados en la interfaz de trading.
 * @type {Object<string, JQuery>}
 */
export const DOMElements = {
    // Contenedor principal del formulario de trading
    form: $('#formulario-trading'),
    // Selector principal de criptomonedas (ej. BTC, ETH)
    selectorPrincipal: $('#cripto'),
    // Desplegable para seleccionar la moneda de pago (en una compra)
    selectorPagarCon: $('#moneda-pago'),
    // Desplegable para seleccionar la moneda a recibir (en una venta)
    selectorRecibirEn: $('#moneda-recibir'),
    // Botón de acción 'Comprar'
    botonComprar: $('.boton-comprar'),
    // Botón de acción 'Vender'
    botonVender: $('.boton-vender'),
    // Botón final 'Confirmar' para la transacción
    botonConfirmar: $('.boton-confirmar'),
    // Input oculto que almacena la acción actual ('comprar' o 'vender')
    inputAccion: $('#accion'),
    // Contenedor para el desplegable 'Pagar con'
    campoPagarCon: $('#campo-pagar-con'),
    // Contenedor para el desplegable 'Recibir en'
    campoRecibirEn: $('#campo-recibir-en'),
    // Span para mostrar el saldo disponible del usuario
    spanSaldoDisponible: $('#saldo-disponible'),
    // Botones de radio para cambiar entre modos de ingreso ('monto' vs 'total')
    radioModoIngreso: $('input[name="modo-ingreso"]'),
    // Etiqueta para el botón de radio 'Cantidad (Cripto)'
    labelModoMonto: $('#label-modo-monto'),
    // Etiqueta para el campo de entrada de monto
    labelMonto: $('label[for="monto"]'),
    // Campo de entrada principal para el monto
    inputMonto: $('#monto'),

};