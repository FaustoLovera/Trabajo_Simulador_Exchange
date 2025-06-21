/**
 * @module pages/billeteraPage
 * @description Orquesta la inicialización y la lógica principal de la página de la billetera,
 * incluyendo la obtención de datos y la renderización de la tabla de activos.
 */

import { fetchEstadoBilletera } from '../services/apiService.js';
import { UIUpdater } from '../components/uiUpdater.js';

/**
 * @typedef {object} Cripto
 * @property {string} ticker - El símbolo de la criptomoneda (ej. "BTC").
 * @property {boolean} es_polvo - Indica si la cantidad es considerada "polvo" (muy pequeña).
 * @property {string} cantidad_formatted - La cantidad de la criptomoneda, formateada como string.
 * @property {string} precio_actual_formatted - El precio actual por unidad, formateado.
 * @property {string} valor_usdt_formatted - El valor total en USDT, formateado.
 * @property {string|number} ganancia_perdida - El valor numérico de la ganancia o pérdida.
 * @property {string} ganancia_perdida_formatted - La ganancia o pérdida, formateada.
 * @property {string} porcentaje_ganancia_formatted - El porcentaje de ganancia o pérdida, formateado.
 * @property {string} porcentaje_formatted - El porcentaje que este activo representa en la billetera, formateado.
 */

/**
 * Crea una fila HTML (`<tr>`) para la tabla de la billetera a partir de un objeto de criptomoneda.
 * @param {Cripto} cripto - El objeto que contiene los datos del activo.
 * @returns {string} Una cadena de texto con el HTML de la fila de la tabla.
 */
function createBilleteraRowHTML(cripto) {
    // Determina la clase CSS para el color basado en si la ganancia/pérdida es positiva o negativa.
    const colorGanancia = parseFloat(cripto.ganancia_perdida) >= 0 ? 'positivo' : 'negativo';
    
    // Utiliza directamente los campos con el sufijo `_formatted` que ya vienen preparados del backend.
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
 * Obtiene los datos de la billetera desde la API y los renderiza en la tabla del DOM.
 * Maneja los estados de carga, éxito y error, actualizando la UI correspondientemente.
 * @async
 * @function renderBilletera
 */
async function renderBilletera() {
    const cuerpoTabla = document.getElementById('tabla-billetera');
    if (!cuerpoTabla) {
        console.warn("El elemento #tabla-billetera no fue encontrado en el DOM. No se renderizará la tabla.");
        return;
    }

    console.log("Cargando datos de la billetera...");
    try {
        const datosBilletera = await fetchEstadoBilletera();

        if (datosBilletera.length === 0) {
            cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
            return;
        }

        const tablaHTML = datosBilletera.map(createBilleteraRowHTML).join('');
        cuerpoTabla.innerHTML = tablaHTML;
        console.log("Billetera renderizada correctamente.");
    } catch (error) {
        console.error('Error al renderizar la billetera:', error);
        // Muestra un mensaje de error tanto en la consola como en la interfaz de usuario.
        UIUpdater.mostrarMensajeError('No se pudieron cargar los datos de la billetera. Por favor, intenta recargar la página.');
        cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar los datos.</td></tr>';
    }
}

/**
 * @description Listener que se ejecuta cuando el DOM está completamente cargado.
 * Inicia el proceso de renderizado de la billetera.
 * @event DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', renderBilletera);