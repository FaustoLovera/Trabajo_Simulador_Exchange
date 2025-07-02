/**
 * @file Gestiona la renderización de la tabla de cotizaciones.
 * @module tablaCotizacionesUI
 * @description Este módulo es responsable de obtener los datos de cotizaciones desde la API,
 * procesarlos para su presentación y renderizar la tabla de criptomonedas en el DOM.
 * También maneja los estados de carga y error.
 */

import { fetchCotizaciones } from '../services/apiService.js';
import { UIUpdater } from './uiUpdater.js';

/** La referencia al cuerpo de la tabla de cotizaciones. */
const cuerpoTabla = document.getElementById('tabla-datos');

/**
 * @typedef {object} CotizacionPresentacion
 * @description Define la estructura de datos de una criptomoneda, ya procesada y formateada
 * por el backend para su visualización directa en la UI.
 * @property {string} logo - URL del ícono de la criptomoneda.
 * @property {string} nombre - Nombre completo de la criptomoneda (ej. "Bitcoin").
 * @property {string} ticker - Símbolo bursátil (ej. "BTC").
 * @property {string} precio_usd_formatted - Precio actual en USD, formateado como cadena.
 * @property {string} '1h_formatted' - Variación porcentual en la última hora, formateada.
 * @property {string} '24h_formatted' - Variación porcentual en las últimas 24 horas, formateada.
 * @property {string} '7d_formatted' - Variación porcentual en los últimos 7 días, formateada.
 * @property {object} perf_1h - Contiene `className` ('positivo'/'negativo') y `arrow` ('▲'/'▼') para el estilo de la variación de 1h.
 * @property {object} perf_24h - Contiene `className` y `arrow` para la variación de 24h.
 * @property {object} perf_7d - Contiene `className` y `arrow` para la variación de 7d.
 * @property {string} market_cap_formatted - Capitalización de mercado, formateada.
 * @property {string} volumen_24h_formatted - Volumen de transacciones en 24h, formateado.
 * @property {string} circulating_supply_formatted - Suministro circulante, formateado.
 */

/**
 * Crea una cadena de texto HTML para una fila (`<tr>`) de la tabla de cotizaciones.
 * Es una función auxiliar pura que transforma un objeto de datos en una representación HTML.
 *
 * @private
 * @param {CotizacionPresentacion} cripto - Objeto con los datos de la criptomoneda a mostrar.
 * @param {number} index - El número de fila, usado para la primera columna (ej. 1, 2, 3...).
 * @returns {string} La cadena HTML que representa la fila de la tabla.
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
 * Obtiene los datos de cotizaciones de la API y renderiza la tabla completa en el DOM.
 * Utiliza `map` y `join` para construir el HTML de forma eficiente. En caso de fallo
 * en la obtención de datos, muestra un mensaje de error en la consola y en la UI.
 * @async
 * @side-effects Modifica el `innerHTML` del elemento '#tabla-datos'.
 */
export async function renderTabla() {
    if (!cuerpoTabla) return;
    try {
        const cotizaciones = (await fetchCotizaciones()) || [];
        const tablaHTML = cotizaciones
            .map((cripto, index) => createFilaCotizacionHTML(cripto, index + 1))
            .join('');
        cuerpoTabla.innerHTML = tablaHTML || '<tr><td colspan="9" class="text-center py-4">No hay datos disponibles.</td></tr>';
    } catch (error) {
        console.error('❌ Error al renderizar la tabla de cotizaciones:', error);
        UIUpdater.mostrarMensajeError(
            'No se pudieron cargar las cotizaciones. La información puede estar desactualizada.'
        );
        cuerpoTabla.innerHTML =
            '<tr><td colspan="9" class="text-center text-danger py-4">Error al cargar las cotizaciones.</td></tr>';
    }
}