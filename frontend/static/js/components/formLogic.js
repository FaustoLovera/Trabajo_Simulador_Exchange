/**
 * @module FormLogic
 * @description Encapsula la lógica principal para manejar las interacciones del usuario
 * y la manipulación de datos dentro del formulario de trading.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { AppState } from '../services/appState.js';

export const FormLogic = {
    /**
     * Rellena un elemento <select> con una lista de opciones. Ahora maneja mejor las listas vacías.
     * @param {JQuery} selector - El objeto jQuery para el elemento <select>.
     * @param {Array<object>} lista - Un array de objetos para crear las opciones.
     * @param {string} valorPorDefecto - El ticker del ítem a seleccionar por defecto.
     * @param {string} [placeholderVacio='No hay opciones'] - Mensaje a mostrar si la lista está vacía.
     */
    popularSelector(selector, lista, valorPorDefecto, placeholderVacio = 'No hay opciones') {
        const valorActual = selector.val();
        selector.empty();

        if (!lista || lista.length === 0) {
            selector.append(new Option(placeholderVacio, '')).prop('disabled', true);
            selector.trigger('change');
            return;
        }

        selector.prop('disabled', false);
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));
        
        let valorFinal;
        if (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) {
            valorFinal = valorPorDefecto;
        } else if (valorActual && lista.some(m => m.ticker === valorActual)) {
            valorFinal = valorActual;
        } else {
            valorFinal = lista[0].ticker;
        }
        
        selector.val(valorFinal).trigger('change');
    },

    /**
     * Orquesta la actualización de todos los selectores del formulario basándose en el estado actual.
     * Esta es la función clave para la lógica dinámica y excluyente.
     */
    actualizarOpcionesDeSelectores() {
        const esCompra = UIState.esModoCompra();
        const tickerPrincipal = UIState.getTickerPrincipal();
        
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();

        if (esCompra) {
            // --- MODO COMPRA ---
            // Selector "Pagar con": Muestra todas las monedas que poseo, excluyendo la que quiero comprar.
            const opcionesPagarCon = ownedCoins.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorPagarCon, opcionesPagarCon, 'USDT', 'No tienes fondos');
        } else {
            // --- MODO VENTA ---
            // Selector "Recibir en": Muestra todas las criptos disponibles, excluyendo la que quiero vender.
            const opcionesRecibirEn = allCryptos.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, opcionesRecibirEn, 'USDT');
        }
    },

    calcularMontoSlider() {
        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();

        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        if (!tickerDeSaldo) return 0;

        const moneda = AppState.getOwnedCoinByTicker(tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.cantidad) : 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};