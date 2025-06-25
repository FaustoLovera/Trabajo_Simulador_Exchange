/**
 * @module uiUpdater
 * @description Centraliza todas las funciones que actualizan dinámicamente la interfaz de usuario.
 * Este módulo es responsable de cambiar la apariencia y el contenido de los elementos del DOM
 * en respuesta a las acciones del usuario y los datos de la aplicación.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
// Importamos AppState para acceder a los datos de la billetera.
import { AppState } from '../services/appState.js';


export const UIUpdater = {
    // ... (las funciones actualizarBotones, actualizarVisibilidadCampos, actualizarLabelMonto no cambian) ...
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

        const etiqueta = esModoMonto ? 'Cantidad' : 'Total';
        DOMElements.labelMonto.text(`${etiqueta} (${tickerRelevante || '...'})`);
    },

    mostrarSaldo(ticker) {
        if (!ticker) {
            DOMElements.spanSaldoDisponible.text('--');
            return;
        }

        // Usamos AppState en lugar de 'window'
        const moneda = AppState.getOwnedCoinByTicker(ticker);
        // Usamos 'cantidad_formatted' para mostrar, que ya viene del backend y es más preciso.
        // Además, nos aseguramos de que el saldo mostrado sea el DISPONIBLE.
        const saldoFormateado = moneda ? moneda.cantidad_formatted : '0.00000000';
        const tickerMostrado = moneda ? moneda.ticker : ticker;
        DOMElements.spanSaldoDisponible.text(`${saldoFormateado} ${tickerMostrado}`);
    },
    
    setInputMonto(valor) {
        DOMElements.inputMonto.val(valor);
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
            })
            .join('');

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
    }
};