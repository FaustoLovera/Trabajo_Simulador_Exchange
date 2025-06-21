// frontend/static/js/components/formLogic.js

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

export const FormLogic = {
    /**
     * Llena un selector de Bootstrap con opciones y selecciona un valor por defecto.
     * @param {jQuery} selector - El elemento selector de jQuery.
     * @param {Array<Object>} lista - Lista de objetos para poblar el selector (cada objeto debe tener 'ticker' y 'nombre').
     * @param {string} valorPorDefecto - El valor a seleccionar por defecto.
     * @returns {string|null} El ticker seleccionado o null si la lista está vacía.
     */
    popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        // CORRECCIÓN: Asegurarse de que se usan las propiedades correctas (ticker, nombre)
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));
        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) ? valorPorDefecto : (lista.length > 0 ? lista[0].ticker : null);
        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        }
        return valorFinal;
    },

    /**
     * Calcula el monto basado en el valor del slider y el saldo disponible.
     * Protegido contra el caso donde window.ownedCoins aún no está cargado.
     * @returns {number} El monto calculado.
     */
    calcularMontoSlider() {
        // Añade este log para verificar si la función se llama
        console.log("DEBUG: Se ha llamado a calcularMontoSlider()"); 

        // ----> CORRECCIÓN DEFENSIVA CLAVE <----
        // Si window.ownedCoins aún no se ha cargado desde la API, no hagas nada y devuelve 0.
        // Esto evita el crash durante la inicialización.
        if (!window.ownedCoins) {
             console.log("DEBUG: window.ownedCoins es undefined. Saliendo de calcularMontoSlider.");
             return 0;
        }
        
        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();
        
        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        
        // Ahora que sabemos que window.ownedCoins existe, podemos usarlo de forma segura.
        const moneda = window.ownedCoins.find(m => m.ticker === tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.cantidad) : 0; // Usar .cantidad
        
        if (!tickerDeSaldo) return 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};