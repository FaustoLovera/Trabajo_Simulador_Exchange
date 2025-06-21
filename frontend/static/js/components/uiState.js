// Gestiona el estado de la interfaz de usuario, como el modo de operación (compra/venta).
import { DOMElements } from './domElements.js';

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