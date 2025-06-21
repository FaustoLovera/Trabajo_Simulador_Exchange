import { formatoValor, formatoCantidad } from './formatters.js';

async function fetchEstadoBilletera() {
    try {
        const response = await fetch('/api/billetera/estado-completo');
        return await response.json();
    } catch (error) {
        console.error('Error al cargar estado de la billetera:', error);
        return [];
    }
}

function createFilaBilleteraHTML(cripto) {
    const colorGanancia = cripto.ganancia_perdida >= 0 ? 'positivo' : 'negativo';
    const cantidadFormateada = cripto.ticker === 'USDT' 
        ? formatoValor(cripto.cantidad, 2, '') 
        : formatoCantidad(cripto.cantidad);

    return `
        <tr>
            <td class="text-center">${cripto.ticker} ${cripto.es_polvo ? '<span class="text-muted small">(polvo)</span>' : ''}</td>
            <td class="text-center">${cantidadFormateada}</td>
            <td class="text-center">${formatoValor(cripto.precio_actual, 6, '')}</td>
            <td class="text-center">${formatoValor(cripto.valor_usdt)}</td>
            <td class="text-center ${colorGanancia}">${formatoValor(cripto.ganancia_perdida)}</td>
            <td class="text-center ${colorGanancia}">${parseFloat(cripto.porcentaje_ganancia).toFixed(2)}%</td>
            <td class="text-center">${parseFloat(cripto.porcentaje).toFixed(2)}%</td>
        </tr>
    `;
}

async function renderBilletera() {
    const cuerpoTabla = document.getElementById('tabla-billetera');
    if (!cuerpoTabla) return;

    const datosBilletera = await fetchEstadoBilletera();
    if (datosBilletera.length === 0) {
        cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
        return;
    }

    const tablaHTML = datosBilletera.map(createFilaBilleteraHTML).join('');
    cuerpoTabla.innerHTML = tablaHTML;
}

document.addEventListener('DOMContentLoaded', renderBilletera);