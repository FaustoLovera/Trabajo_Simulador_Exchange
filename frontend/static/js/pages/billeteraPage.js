/**
 * Obtiene el estado financiero completo de la billetera desde la API.
 * Los datos ya vienen pre-formateados desde el backend.
 * @returns {Promise<Array>}
 */
async function fetchEstadoBilletera() {
    try {
        const response = await fetch('/api/billetera/estado-completo');
        if (!response.ok) {
            throw new Error('Error al cargar estado de la billetera');
        }
        return await response.json();
    } catch (error) {
        console.error('❌ Error al obtener el estado de la billetera:', error);
        return [];
    }
}

/**
 * Crea una fila HTML para la tabla de la billetera a partir de un objeto de cripto.
 * @param {object} cripto - El objeto que contiene los datos de la cripto.
 * @returns {string} El string HTML para la fila <tr>.
 */
function createFilaBilleteraHTML(cripto) {
    // La lógica de color se basa en el valor numérico crudo.
    const colorGanancia = parseFloat(cripto.ganancia_perdida) >= 0 ? 'positivo' : 'negativo';
    
    // Se usan directamente los campos _formatted que vienen del backend.
    return `
        <tr>
            <td class="text-center">${cripto.ticker} ${cripto.es_polvo ? '<span class="text-muted small">(polvo)</span>' : ''}</td>
            <td class="text-center">${cripto.cantidad_formatted}</td>
            <td class="text-center">${cripto.precio_actual_formatted}</td>
            <td class="text-center">${cripto.valor_usdt_formatted}</td>
            <td class="text-center ${colorGanancia}">${cripto.ganancia_perdida_formatted}</td>
            <td class="text-center ${colorGanancia}">${cripto.porcentaje_ganancia_formatted}</td>
            <td class="text-center">${cripto.porcentaje_formatted}</td>
        </tr>
    `;
}

/**
 * Renderiza la tabla completa de la billetera en el DOM.
 */
async function renderBilletera() {
    const cuerpoTabla = document.getElementById('tabla-billetera');
    if (!cuerpoTabla) {
        console.warn("Elemento #tabla-billetera no encontrado.");
        return;
    }

    console.log("🔄 Cargando datos de la billetera...");
    const datosBilletera = await fetchEstadoBilletera();

    if (datosBilletera.length === 0) {
        cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
        return;
    }

    const tablaHTML = datosBilletera.map(createFilaBilleteraHTML).join('');
    cuerpoTabla.innerHTML = tablaHTML;
    console.log("✅ Billetera renderizada correctamente.");
}

// Iniciar el proceso cuando el DOM esté listo.
document.addEventListener('DOMContentLoaded', renderBilletera);