/**
 * @module tablaCotizacionesUI
 * @description Controla la renderización y actualización de la tabla de cotizaciones de criptomonedas.
 */

import { fetchCotizaciones } from '../services/apiService.js';
import { UIUpdater } from './uiUpdater.js';

const cuerpoTabla = document.getElementById('tabla-datos');

/**
 * @typedef {object} CotizacionPresentacion
 * @property {string} logo - URL del logo de la criptomoneda.
 * @property {string} nombre - Nombre de la criptomoneda.
 * @property {string} ticker - Símbolo de la criptomoneda.
 * @property {string} precio_usd_formatted - Precio formateado en USD.
 * @property {string} '1h_formatted' - Variación porcentual formateada (1h).
 * @property {string} '24h_formatted' - Variación porcentual formateada (24h).
 * @property {string} '7d_formatted' - Variación porcentual formateada (7d).
 * @property {object} perf_1h - Objeto con {className, arrow} para rendimiento 1h.
 * @property {object} perf_24h - Objeto con {className, arrow} para rendimiento 24h.
 * @property {object} perf_7d - Objeto con {className, arrow} para rendimiento 7d.
 * @property {string} market_cap_formatted - Capitalización de mercado formateada.
 * @property {string} volumen_24h_formatted - Volumen de 24h formateado.
 * @property {string} circulating_supply_formatted - Suministro circulante formateado.
 */

/**
 * Crea el HTML para una fila de la tabla de cotizaciones a partir de datos ya procesados.
 *
 * @private
 * @param {CotizacionPresentacion} cripto - El objeto de datos de la criptomoneda, ya formateado por el backend.
 * @param {number} index - El número de fila (índice + 1).
 * @returns {string} Una cadena de texto con el HTML del `<tr>` para la criptomoneda.
 */
function createFilaCotizacionHTML(cripto, index) {
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
                <span class="${cripto.perf_1h.className}">
                    <span class="flecha">${cripto.perf_1h.arrow}</span>
                    ${cripto['1h_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${cripto.perf_24h.className}">
                    <span class="flecha">${cripto.perf_24h.arrow}</span>
                    ${cripto['24h_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${cripto.perf_7d.className}">
                    <span class="flecha">${cripto.perf_7d.arrow}</span>
                    ${cripto['7d_formatted']}
                </span>
            </td>
            
            <td class="text-end px-3">${cripto.market_cap_formatted}</td>
            <td class="text-end px-3">${cripto.volumen_24h_formatted}</td>
            <td class="text-end px-3">${cripto.circulating_supply_formatted}</td>
        </tr>
    `;
}

/**
 * Obtiene los datos de cotizaciones y renderiza la tabla en el DOM.
 * Si no hay cotizaciones, la tabla simplemente se mostrará vacía.
 * @async
 * @side-effects Modifica el `innerHTML` del elemento '#tabla-datos'.
 *               Puede mostrar un mensaje de error si la carga de datos falla.
 */
export async function renderTabla() {
    if (!cuerpoTabla) return;
    try {
        const cotizaciones = (await fetchCotizaciones()) || [];
        cuerpoTabla.innerHTML = cotizaciones
            .map((cripto, index) => createFilaCotizacionHTML(cripto, index + 1))
            .join('');
    } catch (error) {
        console.error('❌ Error al renderizar la tabla de cotizaciones:', error);
        UIUpdater.mostrarMensajeError(
            'No se pudieron cargar las cotizaciones. La información puede estar desactualizada.'
        );
        cuerpoTabla.innerHTML =
            '<tr><td colspan="9" class="text-center text-danger py-4">Error al cargar las cotizaciones.</td></tr>';
    }
}