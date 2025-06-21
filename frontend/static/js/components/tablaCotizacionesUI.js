/**
 * @module tablaCotizacionesUI
 * @description Controla la renderización y actualización de la tabla de cotizaciones de criptomonedas.
 */

import { fetchCotizaciones } from '../services/apiService.js';
import { UIUpdater } from './uiUpdater.js';

const cuerpoTabla = document.getElementById('tabla-datos');

/**
 * @typedef {object} Cotizacion
 * @property {string} logo - URL del logo de la criptomoneda.
 * @property {string} nombre - Nombre de la criptomoneda.
 * @property {string} ticker - Símbolo de la criptomoneda.
 * @property {string} precio_usd_formatted - Precio formateado en USD.
 * @property {string} '1h_%' - Variación porcentual en la última hora.
 * @property {string} '24h_%' - Variación porcentual en las últimas 24 horas.
 * @property {string} '7d_%' - Variación porcentual en los últimos 7 días.
 * @property {string} '1h_%_formatted' - Variación porcentual formateada (1h).
 * @property {string} '24h_%_formatted' - Variación porcentual formateada (24h).
 * @property {string} '7d_%_formatted' - Variación porcentual formateada (7d).
 * @property {string} market_cap_formatted - Capitalización de mercado formateada.
 * @property {string} volumen_24h_formatted - Volumen de 24h formateado.
 * @property {string} circulating_supply_formatted - Suministro circulante formateado.
 */

/**
 * Crea el HTML para una fila de la tabla de cotizaciones.
 *
 * @private
 * @param {Cotizacion} cripto - El objeto de datos de la criptomoneda.
 * @param {number} index - El número de fila (índice + 1).
 * @returns {string} Una cadena de texto con el HTML del `<tr>` para la criptomoneda.
 */
function createFilaCotizacionHTML(cripto, index) {
    /**
     * Determina la clase CSS y el símbolo de flecha para valores de rendimiento.
     * @param {string|number} value - El valor numérico a evaluar.
     * @returns {{className: string, arrow: string}} Objeto con la clase ('positivo' o 'negativo') y la flecha ('▲' o '▼').
     */
    const getPerfIndicator = (value) => {
        const isPositive = parseFloat(value) >= 0;
        return {
            className: isPositive ? 'positivo' : 'negativo',
            arrow: isPositive ? '▲' : '▼'
        };
    };

    const perf1h = getPerfIndicator(cripto['1h_%']);
    const perf24h = getPerfIndicator(cripto['24h_%']);
    const perf7d = getPerfIndicator(cripto['7d_%']);

    return `
        <tr>
            <td class="text-start px-3">${index}</td>
            <td class="text-start px-3">
                <img src="${cripto.logo}" width="20" class="logo-cripto" alt="${cripto.ticker} logo">
                <span class="nombre-cripto">${cripto.nombre}</span>
                <span class="ticker-cripto">(${cripto.ticker})</span>
            </td>
            <td class="text-start px-3 fw-bold">${cripto.precio_usd_formatted}</td>
            
            <td class="text-end px-3">
                <span class="${perf1h.className}">
                    <span class="flecha">${perf1h.arrow}</span>
                    ${cripto['1h_%_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${perf24h.className}">
                    <span class="flecha">${perf24h.arrow}</span>
                    ${cripto['24h_%_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${perf7d.className}">
                    <span class="flecha">${perf7d.arrow}</span>
                    ${cripto['7d_%_formatted']}
                </span>
            </td>
            
            <td class="text-end px-3">${cripto.market_cap_formatted}</td>
            <td class="text-end px-3">${cripto.volumen_24h_formatted}</td>
            <td class="text-end px-3">${cripto.circulating_supply_formatted}</td>
        </tr>
    `;
}

/**
 * Obtiene los datos de cotizaciones y renderiza la tabla completa en el DOM.
 * Maneja los estados de carga, éxito y error.
 * @async
 * @side-effects Modifica el `innerHTML` del elemento '#tabla-datos'.
 *               Puede mostrar un mensaje de error global a través de `UIUpdater`.
 */
export async function renderTabla() {
    if (!cuerpoTabla) return;
    try {
        const cotizaciones = await fetchCotizaciones();
        if (!cotizaciones || cotizaciones.length === 0) {
            cuerpoTabla.innerHTML =
                '<tr><td colspan="9" class="text-center text-muted py-4">No hay datos disponibles.</td></tr>';
            return;
        }
        cuerpoTabla.innerHTML = cotizaciones.map((cripto, index) => createFilaCotizacionHTML(cripto, index + 1)).join('');
    } catch (error) {
        console.error('❌ Error al renderizar la tabla de cotizaciones:', error);
        UIUpdater.mostrarMensajeError('No se pudieron cargar las cotizaciones. La información puede estar desactualizada.');
        // Muestra un estado de error en la propia tabla para informar al usuario.
        cuerpoTabla.innerHTML = '<tr><td colspan="9" class="text-center text-danger py-4">Error al cargar las cotizaciones.</td></tr>';
    }
}
