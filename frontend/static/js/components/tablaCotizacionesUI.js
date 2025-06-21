import { fetchCotizacionesJSON } from '../services/cotizacionesApiService.js';

const cuerpoTabla = document.getElementById('tabla-datos');

function createFilaCotizacionHTML(cripto, index) {
    // Lógica para determinar clases y flechas basada en los datos numéricos crudos
    const clase1h = parseFloat(cripto['1h_%']) >= 0 ? 'positivo' : 'negativo';
    const flecha1h = parseFloat(cripto['1h_%']) >= 0 ? '▲' : '▼';

    const clase24h = parseFloat(cripto['24h_%']) >= 0 ? 'positivo' : 'negativo';
    const flecha24h = parseFloat(cripto['24h_%']) >= 0 ? '▲' : '▼';

    const clase7d = parseFloat(cripto['7d_%']) >= 0 ? 'positivo' : 'negativo';
    const flecha7d = parseFloat(cripto['7d_%']) >= 0 ? '▲' : '▼';

    return `
        <tr>
            <td class="text-start px-3">${index}</td>
            <td class="text-start px-3">
                <img src="${cripto.logo}" width="20" class="logo-cripto" alt="${cripto.ticker} logo">
                <span class="nombre-cripto">${cripto.nombre}</span>
                <span class="ticker-cripto">(${cripto.ticker})</span>
            </td>
            <td class="text-start px-3 fw-bold">${cripto.precio_usd_formatted}</td>
            
            <!-- CORRECCIÓN: Envolvemos todo en un span con la clase de color -->
            <td class="text-end px-3">
                <span class="${clase1h}">
                    <span class="${clase1h === 'positivo' ? 'flecha-verde' : 'flecha-roja'}">${flecha1h}</span>
                    ${cripto['1h_%_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${clase24h}">
                    <span class="${clase24h === 'positivo' ? 'flecha-verde' : 'flecha-roja'}">${flecha24h}</span>
                    ${cripto['24h_%_formatted']}
                </span>
            </td>
            <td class="text-end px-3">
                <span class="${clase7d}">
                    <span class="${clase7d === 'positivo' ? 'flecha-verde' : 'flecha-roja'}">${flecha7d}</span>
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
    const cotizaciones = await fetchCotizacionesJSON();
    if (!cotizaciones || cotizaciones.length === 0) {
        cuerpoTabla.innerHTML =
            '<tr><td colspan="9" class="text-center text-muted py-4">No hay datos disponibles.</td></tr>';
        return;
    }
    cuerpoTabla.innerHTML = cotizaciones.map((cripto, index) => createFilaCotizacionHTML(cripto, index + 1)).join('');
}
