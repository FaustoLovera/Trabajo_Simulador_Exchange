/**
 * @module FormLogic
 * @description Encapsula la lógica principal para manejar las interacciones del usuario
 * y la manipulación de datos dentro del formulario de trading.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

/**
 * @typedef {Object} Moneda
 * @property {string} ticker - El símbolo de la moneda (ej. 'BTC').
 * @property {string} nombre - El nombre completo de la moneda (ej. 'Bitcoin').
 */

/**
 * Colección de funciones que gestionan la lógica del formulario de trading.
 */
export const FormLogic = {
    /**
     * Rellena un elemento <select> con una lista de opciones.
     *
     * @param {JQuery} selector - El objeto jQuery para el elemento <select> que se va a rellenar.
     * @param {Moneda[]} lista - Un array de objetos para crear las opciones.
     * @param {string} [valorPorDefecto] - El ticker del ítem que se seleccionará por defecto.
     * @returns {string|null} El ticker del valor finalmente seleccionado, o null si la lista está vacía.
     * @side-effects Limpia y añade elementos <option> al DOM. Dispara un evento 'change'.
     */
    popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));

        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto))
            ? valorPorDefecto
            : (lista.length > 0 ? lista[0].ticker : null);

        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        }
        return valorFinal;
    },

    /**
     * Calcula el monto de la operación basado en el porcentaje del slider.
     *
     * Esta función determina el saldo disponible de la moneda relevante
     * (moneda de pago para compras, moneda principal para ventas) y calcula
     * el monto correspondiente al porcentaje del slider.
     *
     * @returns {number} El monto calculado para la operación.
     */
    calcularMontoSlider() {
        // Comprobación defensiva: si los datos de monedas del usuario aún no se han cargado,
        // devuelve 0 para evitar errores al inicio.
        if (!window.ownedCoins) {
            return 0;
        }

        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();

        // Determina qué saldo de moneda usar según la dirección de la operación.
        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        if (!tickerDeSaldo) return 0;

        // Busca la moneda específica en la billetera del usuario y obtiene su cantidad disponible.
        const moneda = window.ownedCoins.find(m => m.ticker === tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.cantidad) : 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};