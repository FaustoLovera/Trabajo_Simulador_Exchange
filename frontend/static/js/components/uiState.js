import { DOMElements } from './domElements.js';

// Mantiene y provee el estado actual de la UI, desacoplando la lógica de la lectura directa del DOM.
export const UIState = {
    esModoCompra() {
        return DOMElements.inputAccion.val() === 'comprar';
    },
    getModoIngreso() {
        return DOMElements.radioModoIngreso.filter(':checked').val();
    },
    getTickerPrincipal() {
        return DOMElements.selectorPrincipal.val();
    },
    getTickerPago() {
        return DOMElements.selectorPagarCon.val();
    },
    getTickerRecibo() {
        return DOMElements.selectorRecibirEn.val();
    }
};