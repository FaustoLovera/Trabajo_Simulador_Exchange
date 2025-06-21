/**
 * @module uiUpdater
 * @description Centraliza todas las funciones que actualizan dinámicamente la interfaz de usuario.
 * Este módulo es responsable de cambiar la apariencia y el contenido de los elementos del DOM
 * en respuesta a las acciones del usuario y los datos de la aplicación.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';

/**
 * @description Objeto que agrupa métodos para manipular la interfaz de usuario.
 * @exports UIUpdater
 */
export const UIUpdater = {
    /**
     * Actualiza el texto y estilo de los botones de acción (comprar/vender) según el modo actual.
     * @side-effects Modifica el texto y las clases CSS de `botonConfirmar`, `botonComprar` y `botonVender`.
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
     * Muestra u oculta los campos de 'Pagar con' y 'Recibir en' según el modo de operación.
     * @side-effects Modifica la visibilidad y el estado `disabled` de los selectores correspondientes.
     */
    actualizarVisibilidadCampos() {
        const esCompra = UIState.esModoCompra();
        DOMElements.campoPagarCon.toggle(esCompra);
        DOMElements.campoRecibirEn.toggle(!esCompra);
        DOMElements.selectorPagarCon.prop('disabled', !esCompra);
        DOMElements.selectorRecibirEn.prop('disabled', esCompra);
    },

    /**
     * Actualiza la etiqueta del campo de monto/cantidad para reflejar la moneda relevante.
     * @side-effects Modifica el texto de `labelMonto`.
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
     * Muestra el saldo disponible para una moneda específica.
     * Se asegura de que el objeto `window.ownedCoins` esté disponible antes de intentar leerlo.
     * @param {string} ticker - El ticker de la moneda para la cual mostrar el saldo.
     * @side-effects Modifica el texto de `spanSaldoDisponible`.
     */
    mostrarSaldo(ticker) {
        if (!ticker) {
            DOMElements.spanSaldoDisponible.text('--');
            return;
        }

        // Es crucial que 'window.ownedCoins' exista para evitar errores de referencia.
        if (!window.ownedCoins) {
            console.warn('Intento de mostrar saldo antes de que window.ownedCoins esté listo.');
            DOMElements.spanSaldoDisponible.text('Cargando...');
            return;
        }

        const moneda = window.ownedCoins.find((m) => m.ticker === ticker);
        const saldoFormateado = moneda ? moneda.cantidad_formatted : '0.00000000';
        DOMElements.spanSaldoDisponible.text(`${saldoFormateado} ${ticker}`);
    },

    /**
     * Establece el valor del campo de entrada de monto.
     * @param {string|number} valor - El valor a establecer en el input.
     * @side-effects Modifica el valor de `inputMonto`.
     */
    setInputMonto(valor) {
        DOMElements.inputMonto.val(valor);
    },

    /**
     * Reinicia el control deslizante de monto a su valor inicial (0).
     * @side-effects Modifica el valor de `sliderMonto`.
     */
    resetSlider() {
        DOMElements.sliderMonto.val(0);
    },

    /**
     * Renderiza la tabla del historial de transacciones.
     * @param {Array<object>} historialData - Un array de objetos de transacciones.
     * @side-effects Modifica el `innerHTML` de `tabla-historial`.
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

    /**
     * Muestra un mensaje de error en un contenedor específico de la UI.
     * @param {string} mensaje - El mensaje de error a mostrar.
     * @param {string} [containerSelector='#error-container'] - El selector del contenedor donde se mostrará el error.
     * @side-effects Modifica el `innerHTML` del contenedor de errores.
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
