/**
 * @module pages/billeteraPage
 * @description Orquesta la inicialización y la lógica principal de la página de la billetera,
 * incluyendo la obtención de datos y la renderización de la tabla de activos y comisiones.
 */

// Importamos la nueva función para obtener comisiones junto con la existente.
import { fetchEstadoBilletera, fetchComisiones } from '../services/apiService.js';
import { UIUpdater } from '../components/uiUpdater.js';

/**
 * @typedef {object} ActivoBilletera
 * @property {string} ticker - El símbolo de la criptomoneda (ej. "BTC").
 * @property {boolean} es_polvo - Indica si la cantidad es considerada "polvo" (muy pequeña).
 * @property {string} cantidad_formatted - La cantidad de la criptomoneda, formateada como string.
 * @property {string} precio_actual_formatted - El precio actual por unidad, formateado.
 * @property {string} valor_usdt_formatted - El valor total en USDT, formateado.
 * @property {string|number} ganancia_perdida - El valor numérico de la ganancia o pérdida.
 * @property {string} ganancia_perdida_formatted - La ganancia o pérdida, formateada.
 * @property {string} porcentaje_ganancia_formatted - El porcentaje de ganancia o pérdida, formateado.
 * @property {string} porcentaje_formatted - El porcentaje que este activo representa en la billetera.
 */

/**
 * Crea una fila HTML (`<tr>`) para la tabla de la billetera.
 * @param {ActivoBilletera} cripto - El objeto que contiene los datos del activo.
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
 * Obtiene los datos de la billetera desde la API y los renderiza en la tabla.
 */
async function renderBilletera() {
    const cuerpoTabla = document.getElementById('tabla-billetera');
    if (!cuerpoTabla) {
        console.warn("El elemento #tabla-billetera no fue encontrado en el DOM.");
        return;
    }

    try {
        const datosBilletera = await fetchEstadoBilletera();
        if (!datosBilletera || datosBilletera.length === 0) {
            cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
        } else {
            cuerpoTabla.innerHTML = datosBilletera.map(createBilleteraRowHTML).join('');
        }
    } catch (error) {
        console.error('Error al renderizar la billetera:', error);
        UIUpdater.mostrarMensajeError('No se pudieron cargar los datos de la billetera.');
        cuerpoTabla.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar los datos.</td></tr>';
    }
}

/**
 * Crea una fila HTML para la tabla de historial de comisiones.
 * @param {object} comision - El objeto de datos de la comisión.
 * @returns {string} Una cadena de texto con el HTML de la fila.
 */
function createComisionRowHTML(comision) {
    // Formatea la fecha para que sea legible.
    const fecha = new Date(comision.timestamp).toLocaleString('es-AR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });

    return `
        <tr>
            <td>${fecha}</td>
            <td>${comision.ticker}</td>
            <td>${parseFloat(comision.cantidad).toFixed(8)}</td>
            <td>$${parseFloat(comision.valor_usd).toFixed(2)}</td>
        </tr>
    `;
}

/**
 * Obtiene los datos de comisiones desde la API y los renderiza en la tabla.
 */
async function renderComisiones() {
    const cuerpoTabla = document.getElementById('tabla-comisiones');
    if (!cuerpoTabla) {
        console.warn("El elemento #tabla-comisiones no fue encontrado en el DOM.");
        return;
    }

    try {
        const datosComisiones = await fetchComisiones();
        if (!datosComisiones || datosComisiones.length === 0) {
            cuerpoTabla.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No se han cobrado comisiones.</td></tr>';
        } else {
            cuerpoTabla.innerHTML = datosComisiones.map(createComisionRowHTML).join('');
        }
    } catch (error) {
        console.error('Error al renderizar las comisiones:', error);
        cuerpoTabla.innerHTML = '<tr><td colspan="4" class="text-center text-danger py-4">Error al cargar las comisiones.</td></tr>';
    }
}

/**
 * Listener que se ejecuta cuando el DOM está completamente cargado.
 * Inicia el renderizado de AMBAS tablas en paralelo para mejorar el rendimiento.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log("Página de Billetera cargada. Obteniendo datos...");
    
    // Usamos Promise.all para que ambas peticiones a la API se realicen
    // de forma concurrente, en lugar de una después de la otra.
    Promise.all([
        renderBilletera(),
        renderComisiones()
    ]);
});