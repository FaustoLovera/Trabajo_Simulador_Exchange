// Orquesta la inicialización y la lógica principal de la página de la billetera.
import { fetchEstadoBilletera } from '../services/apiService.js';
import { UIUpdater } from '../components/uiUpdater.js';

/**
 * Crea una fila HTML para la tabla de la billetera a partir de un objeto de cripto.
 * @param {object} cripto - El objeto que contiene los datos de la cripto.
 * @returns {string} El string HTML para la fila <tr>.
 */
function createBilleteraRowHTML(cripto) {
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
    try {
        const datosBilletera = await fetchEstadoBilletera();

        if (datosBilletera.length === 0) {
            cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
            return;
        }

        const tablaHTML = datosBilletera.map(createBilleteraRowHTML).join('');
        cuerpoTabla.innerHTML = tablaHTML;
        console.log("✅ Billetera renderizada correctamente.");
    } catch (error) {
        console.error('❌ Error al renderizar la billetera:', error);
        // Muestra el error en la consola, en la UI global y en la tabla misma.
        UIUpdater.mostrarMensajeError('No se pudieron cargar los datos de la billetera. Por favor, intenta recargar la página.');
        cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar los datos.</td></tr>';
    }
}

// Iniciar el proceso cuando el DOM esté listo.
document.addEventListener('DOMContentLoaded', () => {renderBilletera()});