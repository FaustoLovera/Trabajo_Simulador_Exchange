/**
 * @file Proporciona una capa de abstracción para leer el estado de la UI.
 * @module UIState
 * @description Este módulo centraliza la lógica para consultar el estado actual de los elementos
 * de la interfaz de usuario. Actúa como una "fuente de verdad" para otros componentes,
 * permitiéndoles obtener datos de la UI sin interactuar directamente con el DOM.
 */

import { DOMElements } from './domElements.js';

/**
 * @namespace UIState
 * @description Agrupa un conjunto de funciones "getter" para consultar el estado actual
 * de los elementos del formulario de trading y otros componentes de la UI.
 */
export const UIState = {
    /**
     * Determina si el modo de operación actual es 'compra'.
     * @returns {boolean} `true` si la acción es 'compra', de lo contrario `false`.
     */
    esModoCompra() {
        return DOMElements.inputAccion.val() === 'compra';
    },

    /**
     * Obtiene el modo de ingreso seleccionado (ej. 'monto' o 'total').
     * @returns {string} El valor del `radio button` de modo de ingreso que esté seleccionado.
     */
    getModoIngreso() {
        return DOMElements.radioModoIngreso.filter(':checked').val();
    },

    /**
     * Obtiene el ticker de la criptomoneda principal seleccionada en el formulario.
     * @returns {string} El ticker de la criptomoneda (ej. 'BTC', 'ETH').
     */
    getTickerPrincipal() {
        return DOMElements.selectorPrincipal.val();
    },

    /**
     * Obtiene el ticker de la moneda seleccionada en el campo 'Pagar con'.
     * @returns {string} El ticker de la moneda de pago (ej. 'USDT').
     */
    getTickerPago() {
        return DOMElements.selectorPagarCon.val();
    },

    /**
     * Obtiene el ticker de la moneda seleccionada en el campo 'Recibir en'.
     * @returns {string} El ticker de la moneda de recibo (ej. 'USDT').
     */
    getTickerRecibo() {
        return DOMElements.selectorRecibirEn.val();
    }
};