// Encapsula la lógica de negocio del formulario de trading.
import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

export const FormLogic = {
    popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        lista.forEach(({ nombre, ticker }) => selector.append(new Option(nombre, ticker)));
        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) ? valorPorDefecto : (lista.length > 0 ? lista[0].ticker : null);
        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        }
        return valorFinal;
    },

    calcularMontoSlider() {
        const porcentaje = parseFloat(DOMElements.sliderMonto.val());
        const esCompra = UIState.esModoCompra();
        
        const tickerDeSaldo = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        // Asumiendo que window.monedasPropias contiene los saldos.
        const moneda = window.monedasPropias.find(m => m.ticker === tickerDeSaldo);
        const saldoDisponible = moneda ? parseFloat(moneda.saldo) : 0;
        
        if (!tickerDeSaldo) return 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};