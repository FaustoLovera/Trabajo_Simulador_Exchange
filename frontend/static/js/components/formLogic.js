/**
 * @module FormLogic
 * @description Encapsula la lógica principal para manejar las interacciones del usuario
 * y la manipulación de datos dentro del formulario de trading.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
// Importamos AppState para acceder a los datos de la billetera.
import { AppState } from '../services/appState.js';

/**
 * @typedef {Object} Moneda
 * @property {string} ticker - El símbolo de la moneda (ej. 'BTC').
 * @property {string} nombre - El nombre completo de la moneda (ej. 'Bitcoin').
 */

export const FormLogic = {
    popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        if (!lista || lista.length === 0) {
            selector.append(new Option('No hay opciones', '')).prop('disabled', true);
            return null;
        }

        selector.prop('disabled', false);
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));

        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto))
            ? valorPorDefecto
            : lista[0].ticker;

        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        }
        return valorFinal;
    },

    calcularMontoSlider() {
        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();

        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        if (!tickerDeSaldo) return 0;

        // Usamos AppState en lugar de 'window' para obtener la moneda.
        const moneda = AppState.getOwnedCoinByTicker(tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.cantidad) : 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};