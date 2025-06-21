import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

// Contiene la lógica de negocio del formulario, como poblar selectores y cálculos.
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
        const saldoDisponible = parseFloat(window.billetera[tickerDeSaldo] || '0');
        
        if (!tickerDeSaldo) return 0;

        return (saldoDisponible * porcentaje) / 100.0;
    }
};