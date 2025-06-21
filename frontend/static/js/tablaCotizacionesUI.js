import { fetchCotizacionesJSON } from './cotizacionesApiService.js';
// Importamos las nuevas funciones de formato
import { formatoValor, formatarNumeroGrande, formatarPorcentajeConColor } from './formatters.js';

const cuerpoTabla = document.getElementById('tabla-datos');

/**
 * Crea una fila de la tabla (un string HTML) a partir de un objeto de cotización.
 * @param {object} cripto - El objeto con los datos de una criptomoneda.
 * @param {number} index - El índice de la fila.
 * @returns {string} El string HTML para la fila <tr>.
 */
function createFilaCotizacionHTML(cripto, index) {
    // La lógica de clases ahora está dentro de la función de formato.

    return `
        <tr>
            <td class="text-start px-3">${index}</td>
            <td class="text-start px-3">
                <img src="${cripto.logo}" width="20" class="logo-cripto" alt="${cripto.ticker} logo">
                <span class="nombre-cripto">${cripto.nombre}</span>
                <span class="ticker-cripto">(${cripto.ticker})</span>
            </td>
            <td class="text-start px-3 fw-bold">${formatoValor(cripto.precio_usd, 2)}</td>
            
            <!-- Usamos la nueva función para formatear los porcentajes -->
            <td class="text-end px-3">${formatarPorcentajeConColor(cripto['1h_%'])}</td>
            <td class="text-end px-3">${formatarPorcentajeConColor(cripto['24h_%'])}</td>
            <td class="text-end px-3">${formatarPorcentajeConColor(cripto['7d_%'])}</td>
            
            <!-- Usamos la nueva función para formatear los números grandes -->
            <td class="text-end px-3">${formatarNumeroGrande(cripto.market_cap)}</td>
            <td class="text-end px-3">${formatarNumeroGrande(cripto.volumen_24h)}</td>

            <!-- Para el suministro, usamos el formato de número con comas y el ticker -->
            <td class="text-end px-3">${parseFloat(cripto.circulating_supply).toLocaleString('en-US', {maximumFractionDigits: 0})} ${cripto.ticker}</td>
        </tr>
    `;
}

/**
 * Obtiene los datos JSON de la API y renderiza la tabla completa.
 */
export async function renderTabla() {
    if (!cuerpoTabla) return;
    
    console.log("🔄 Cargando datos JSON de la tabla...");
    const cotizaciones = await fetchCotizacionesJSON();
    
    if (cotizaciones.length === 0) {
        cuerpoTabla.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">No hay datos disponibles.</td></tr>';
        return;
    }

    const tablaHTML = cotizaciones.map((cripto, index) => createFilaCotizacionHTML(cripto, index + 1)).join('');
    cuerpoTabla.innerHTML = tablaHTML;
    console.log("✅ Tabla de cotizaciones renderizada desde JSON con formato completo.");
}