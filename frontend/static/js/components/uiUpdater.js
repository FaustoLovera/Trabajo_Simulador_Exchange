// frontend/static/js/components/uiUpdater.js

// Contiene funciones para actualizar dinámicamente la interfaz de usuario.
import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

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
        
        // ----> CORRECCIÓN DEFINITIVA <----
        // Usar la variable correcta 'window.ownedCoins' en lugar de 'window.monedasPropias'.
        // También nos aseguramos de que 'window.ownedCoins' exista para evitar errores.
        if (!window.ownedCoins) {
            console.warn("Intento de mostrar saldo antes de que window.ownedCoins esté listo.");
            DOMElements.spanSaldoDisponible.text('Cargando...');
            return;
        }

        const moneda = window.ownedCoins.find(m => m.ticker === ticker);
        const saldoFormateado = moneda ? moneda.cantidad_formatted : '0.00000000';
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
            tablaHistorial.html('<tr><td colspan="5" class="text-center text-muted py-3">No hay transacciones en el historial.</td></tr>');
            return;
        }

        const historialHTML = historialData.map((item) => {
            const claseTipo = item.tipo === 'compra' ? 'text-success' : 'text-danger';

            return `
                <tr>
                    <td class="text-start ps-3">${item.fecha_formatted}</td>
                    <td class="fw-bold">${item.par_formatted}</td>
                    <td class="${claseTipo}">${item.tipo_formatted}</td>
                    <td>${item.cantidad_formatted}</td>
                    <td>${item.valor_total_formatted}</td>
                </tr>
            `;
        }).join('');

        tablaHistorial.html(historialHTML);
    },
    
    mostrarMensajeError(mensaje, containerSelector = '#error-container') {
        const errorContainer = $(containerSelector);
        if (!errorContainer.length) {
            console.error(`Error container '${containerSelector}' not found.`);
            return;
        }
        const alertHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        errorContainer.html(alertHTML);
    },
};