// frontend/static/js/components/formLogic.js

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

export const FormLogic = {
    popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        lista.forEach(({ ticker, nombre }) => selector.append(new Option(`${nombre} (${ticker})`, ticker)));
        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) ? valorPorDefecto : (lista.length > 0 ? lista[0].ticker : null);
        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        }
        return valorFinal;
    },

    calcularMontoSlider() {
        // ----> CORRECCIÓN DEFENSIVA <----
        // Si window.ownedCoins aún no está cargado, devuelve 0 para evitar el crash.
        if (!window.ownedCoins) {
            return 0;
        }
        
        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();
        
        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        
        // ----> CORRECCIÓN DEFINITIVA <----
        // Usar la variable correcta 'window.ownedCoins' en lugar de 'window.monedasPropias'.
        const moneda = window.ownedCoins.find(m => m.ticker === tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.cantidad) : 0;
        
        if (!tickerDeSaldo) return 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};