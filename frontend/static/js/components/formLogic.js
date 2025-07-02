/**
 * @file Gestiona la lógica de negocio del formulario de trading.
 * @module FormLogic
 * @description Este módulo contiene las funciones responsables de actualizar dinámicamente
 * los campos del formulario de trading, como los menús desplegables, basándose en el estado
 * actual de la aplicación (ej. monedas poseídas, acción de compra/venta).
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { AppState } from '../services/appState.js';

/**
 * @namespace FormLogic
 * @description Agrupa funciones que aplican la lógica de negocio a los elementos del formulario.
 */
export const FormLogic = {
    /**
     * Rellena un elemento <select> con una lista de opciones.
     * Si la lista está vacía, muestra un mensaje y deshabilita el selector.
     *
     * @param {JQuery} selector - El objeto jQuery del elemento <select> a rellenar.
     * @param {Array<Object>} lista - Un array de objetos, cada uno con `ticker` y `nombre`.
     * @param {string} [placeholderVacio='No hay opciones'] - Mensaje a mostrar si la lista está vacía.
     */
    popularSelector(selector, lista, placeholderVacio = 'No hay opciones') {
        selector.empty();

        if (!lista || lista.length === 0) {
            selector.append(new Option(placeholderVacio, '')).prop('disabled', true);
            return;
        }

        selector.prop('disabled', false);
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));
    },

    /**
     * Orquesta la actualización de los selectores 'Pagar con' y 'Recibir en' basándose
     * en la acción actual (compra/venta) y los datos del estado de la aplicación.
     * - En modo 'compra', el selector 'Pagar con' muestra las monedas que el usuario posee.
     * - En modo 'venta', el selector 'Recibir en' muestra todas las criptomonedas disponibles.
     */
    actualizarOpcionesDeSelectores() {
        const esCompra = UIState.esModoCompra();
        const tickerPrincipal = UIState.getTickerPrincipal();
        
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();

        if (esCompra) {
            // Filtrar para no poder pagar con la misma moneda que se compra.
            const opcionesPagarCon = ownedCoins.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorPagarCon, opcionesPagarCon, 'No tienes fondos');
            DOMElements.selectorPagarCon.val('USDT'); // Valor por defecto

        } else { // Es modo venta
            // Filtrar para no poder recibir en la misma moneda que se vende.
            const opcionesRecibirEn = allCryptos.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, opcionesRecibirEn);
            DOMElements.selectorRecibirEn.val('USDT'); // Valor por defecto
        }
    }
};