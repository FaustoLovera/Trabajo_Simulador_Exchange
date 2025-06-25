// frontend/static/js/components/formLogic.js

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { AppState } from '../services/appState.js';

export const FormLogic = {
    /**
     * Rellena un elemento <select> con una lista de opciones, SIN disparar eventos.
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
     * Orquesta la actualización de todos los selectores del formulario.
     */
    actualizarOpcionesDeSelectores() {
        const esCompra = UIState.esModoCompra();
        const tickerPrincipal = UIState.getTickerPrincipal();
        
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();

        if (esCompra) {
            const opcionesPagarCon = ownedCoins.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorPagarCon, opcionesPagarCon, 'No tienes fondos');
            // Establecemos el valor por defecto para 'Pagar con' sin disparar el change todavía
            DOMElements.selectorPagarCon.val('USDT');

        } else {
            const opcionesRecibirEn = allCryptos.filter(c => c.ticker !== tickerPrincipal);
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, opcionesRecibirEn);
            // Establecemos el valor por defecto para 'Recibir en'
            DOMElements.selectorRecibirEn.val('USDT');
        }
    }
};