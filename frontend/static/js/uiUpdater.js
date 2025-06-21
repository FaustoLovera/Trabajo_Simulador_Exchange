import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { formatoValor, formatoCantidad } from './formatters.js';

// Contiene todas las funciones que modifican visualmente el DOM.
export const UIUpdater = {
    actualizarBotones() {
        const esCompra = UIState.esModoCompra();
        DOMElements.botonConfirmar
            .text(esCompra ? 'COMPRAR' : 'VENDER')
            .toggleClass('btn-success', esCompra)
            .toggleClass('btn-danger', !esCompra);
        DOMElements.botonComprar
            .toggleClass('active btn-success', esCompra)
            .toggleClass('btn-outline-secondary', !esCompra);
        DOMElements.botonVender
            .toggleClass('active btn-danger', !esCompra)
            .toggleClass('btn-outline-secondary', esCompra);
    },

    actualizarVisibilidadCampos() {
        const esCompra = UIState.esModoCompra();
        DOMElements.campoPagarCon.toggle(esCompra);
        DOMElements.campoRecibirEn.toggle(!esCompra);
        DOMElements.selectorPagarCon.prop('disabled', !esCompra);
        DOMElements.selectorRecibirEn.prop('disabled', esCompra);
    },

    actualizarLabelMonto() {
        const esModoMonto = UIState.getModoIngreso() === 'monto';
        const esCompra = UIState.esModoCompra();
        let tickerRelevante = '';

        if (esCompra) {
            tickerRelevante = esModoMonto ? UIState.getTickerPrincipal() : UIState.getTickerPago();
        } else {
            tickerRelevante = esModoMonto ? UIState.getTickerPrincipal() : UIState.getTickerRecibo();
        }

        const etiqueta = esModoMonto ? 'Monto' : 'Total';
        DOMElements.labelMonto.text(`${etiqueta} (${tickerRelevante || '...'})`);
    },

    mostrarSaldo(ticker) {
        if (!ticker) {
            DOMElements.spanSaldoDisponible.text('--');
            return;
        }
        // Asume que 'billetera' es una variable global disponible (desde el HTML)
        const saldo = window.billetera[ticker] || '0.00';
        const saldoFormateado = parseFloat(saldo).toFixed(8);
        DOMElements.spanSaldoDisponible.text(`${saldoFormateado} ${ticker}`);
    },

    setInputMonto(valor) {
        DOMElements.inputMonto.val(valor);
    },

    resetSlider() {
        DOMElements.sliderMonto.val(0);
    },

    renderHistorial(historialData) {
        const tablaHistorial = $('#tabla-historial');
        if (!tablaHistorial.length) return;

        if (historialData.length === 0) {
            tablaHistorial.html(
                '<tr><td colspan="5" class="text-center text-muted py-3">No hay transacciones en el historial.</td></tr>'
            );
            return;
        }

        const historialHTML = historialData
            .map((item) => {
                const fecha = new Date(item.timestamp).toLocaleDateString();
                const hora = new Date(item.timestamp).toLocaleTimeString();
                const claseTipo = item.tipo === 'compra' ? 'text-success' : 'text-danger';
                const par =
                    item.tipo === 'compra'
                        ? `${item.destino.ticker}/${item.origen.ticker}`
                        : `${item.origen.ticker}/${item.destino.ticker}`;
                const cantidad = item.tipo === 'compra' ? item.destino.cantidad : item.origen.cantidad;
                const tickerCantidad = item.tipo === 'compra' ? item.destino.ticker : item.origen.ticker;

                return `
                <tr>
                    <td class="text-start ps-3">${fecha} <span class="text-white-50">${hora}</span></td>
                    <td class="fw-bold">${par}</td>
                    <td class="${claseTipo}">${item.tipo.charAt(0).toUpperCase() + item.tipo.slice(1)}</td>
                    <td>${formatoCantidad(cantidad)} ${tickerCantidad}</td>
                    <td>${formatoValor(item.valor_usd)}</td>
                </tr>
            `;
            })
            .join('');

        tablaHistorial.html(historialHTML);
    },
};
