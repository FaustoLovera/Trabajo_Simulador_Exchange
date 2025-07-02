/**
 * @file Centraliza todas las funciones que modifican el DOM para actualizar la interfaz.
 * @module UIUpdater
 * @description Este módulo es el responsable exclusivo de realizar cambios visuales en la UI.
 * Contiene funciones que manipulan directamente los elementos del DOM para reflejar el estado
 * actual de la aplicación, como cambiar colores, texto, visibilidad y renderizar datos.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { AppState } from '../services/appState.js';

/**
 * @namespace UIUpdater
 * @description Agrupa funciones que realizan actualizaciones directas en el DOM.
 */
export const UIUpdater = {
    /**
     * Ajusta los colores y el texto de los botones de acción (Comprar/Vender)
     * según el modo de trading actual.
     * @effects Modifica las clases CSS y el texto de los botones de confirmar, comprar y vender.
     */
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

    /**
     * Muestra u oculta los campos 'Pagar con' y 'Recibir en' basándose en si la operación
     * es una compra o una venta.
     * @effects Modifica la visibilidad y el estado `disabled` de los selectores de pago y recibo.
     */
    actualizarVisibilidadCampos() {
        const esCompra = UIState.esModoCompra();
        DOMElements.campoPagarCon.toggle(esCompra);
        DOMElements.campoRecibirEn.toggle(!esCompra);
        DOMElements.selectorPagarCon.prop('disabled', !esCompra);
        DOMElements.selectorRecibirEn.prop('disabled', esCompra);
    },

    /**
     * Actualiza la etiqueta del campo de monto principal para indicar si se ingresa
     * una 'Cantidad' de cripto o un 'Total' de la moneda de pago/recibo.
     * @effects Cambia el texto del `label` del campo de monto.
     */
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

    /**
     * Actualiza las etiquetas de los radio buttons 'Cantidad' y 'Total' para mostrar
     * a qué moneda se refiere cada opción en el contexto actual.
     * @effects Cambia el texto de los `label` de los radio buttons de modo de ingreso.
     */
    actualizarLabelsModoIngreso() {
        const tickerPrincipal = UIState.getTickerPrincipal();
        let tickerSecundario;

        if (UIState.esModoCompra()) {
            tickerSecundario = UIState.getTickerPago();
        } else {
            tickerSecundario = UIState.getTickerRecibo();
        }
        
        DOMElements.labelModoMonto.text(`Cantidad (${tickerPrincipal || 'Cripto'})`);
        DOMElements.labelModoTotal.text(`Total (${tickerSecundario || 'USDT'})`);
    },

    /**
     * Muestra el saldo disponible para una moneda específica.
     * @param {string} ticker - El ticker de la moneda cuyo saldo se mostrará (ej. 'BTC', 'USDT').
     * @effects Actualiza el texto del `span` de saldo disponible.
     */
    mostrarSaldo(ticker) {
        if (!ticker) {
            DOMElements.spanSaldoDisponible.text('--');
            return;
        }

        const moneda = AppState.getOwnedCoinByTicker(ticker);
        const saldoFormateado = moneda ? moneda.cantidad_disponible_formatted : '0.00';
        
        DOMElements.spanSaldoDisponible.text(`${saldoFormateado} ${ticker}`); 
    },
    
    /**
     * Establece el valor del campo de entrada de monto.
     * @param {string|number} valor - El valor a establecer en el input.
     * @effects Modifica el valor del `input` de monto.
     */
    setInputMonto(valor) {
        DOMElements.inputMonto.val(valor);
    },

    /**
     * Renderiza la tabla del historial de transacciones.
     * @param {Array<object>} historialData - Un array de objetos con los datos de las transacciones.
     * @effects Reemplaza el contenido del `tbody` de la tabla de historial.
     */
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
                const claseTipo = item.tipo.toLowerCase() === 'compra' ? 'text-success' : 'text-danger';

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

    /**
     * Muestra un mensaje de error en un contenedor específico de la UI.
     * @param {string} mensaje - El mensaje de error a mostrar.
     * @param {string} [containerSelector='#error-container'] - El selector del contenedor donde se mostrará el error.
     * @effects Inserta un `div` de alerta de Bootstrap en el contenedor especificado.
     */
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