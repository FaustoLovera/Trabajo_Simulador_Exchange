/**
 * @module uiState
 * @description Proporciona un objeto centralizado para consultar el estado actual de la interfaz de usuario.
 * Este módulo abstrae la lógica de acceso a los valores de los elementos del DOM, facilitando
 * la obtención de información sobre el estado de la UI sin interactuar directamente con `DOMElements`.
 */

import { DOMElements } from './domElements.js';

/**
 * @description Un objeto que agrupa funciones para obtener diferentes aspectos del estado de la UI.
 * Cada método consulta un elemento del DOM a través de `DOMElements` y devuelve su estado actual.
 * @exports UIState
 */
export const UIState = {
    /**
     * Comprueba si el modo de operación actual es 'comprar'.
     * @returns {boolean} `true` si la acción seleccionada es 'comprar', de lo contrario `false`.
     */
    esModoCompra() {
        return DOMElements.inputAccion.val() === 'comprar';
    },

    /**
     * Obtiene el modo de ingreso seleccionado (ej. 'cantidad' o 'monto').
     * @returns {string} El valor del radio button seleccionado para el modo de ingreso.
     */
    getModoIngreso() {
        return DOMElements.radioModoIngreso.filter(':checked').val();
    },

    /**
     * Obtiene el ticker de la criptomoneda principal seleccionada.
     * @returns {string} El ticker de la criptomoneda en el selector principal.
     */
    getTickerPrincipal() {
        return DOMElements.selectorPrincipal.val();
    },

    /**
     * Obtiene el ticker de la moneda utilizada para pagar.
     * @returns {string} El ticker de la moneda en el selector 'pagar con'.
     */
    getTickerPago() {
        return DOMElements.selectorPagarCon.val();
    },

    /**
     * Obtiene el ticker de la moneda que se recibirá.
     * @returns {string} El ticker de la moneda en el selector 'recibir en'.
     */
    getTickerRecibo() {
        return DOMElements.selectorRecibirEn.val();
    }
};