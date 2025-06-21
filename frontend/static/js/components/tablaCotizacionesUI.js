// Controla la renderización y actualización de la tabla de cotizaciones.

import { fetchCotizaciones } from '../services/apiService.js';
import { UIUpdater } from './uiUpdater.js';

const cuerpoTabla = document.getElementById('tabla-datos');

function createFilaCotizacionHTML(cripto, index) {
    // Helper para no repetir la lógica de positivo/negativo
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
        // Opcional: mostrar un estado de error en la propia tabla
        cuerpoTabla.innerHTML = '<tr><td colspan="9" class="text-center text-danger py-4">Error al cargar las cotizaciones.</td></tr>';
    }
}
