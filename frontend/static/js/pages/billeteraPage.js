/**
 * @file Punto de entrada y controlador para la página de la billetera (`billetera.html`).
 * @module pages/billeteraPage
 * @description Este script orquesta la inicialización de la página de la billetera, obteniendo
 * y renderizando el estado de los activos y el historial de comisiones. También gestiona
 * la interactividad de la página, como el filtro para ocultar activos de bajo valor ("polvo").
 */

import { fetchEstadoBilletera, fetchComisiones } from '../services/apiService.js';
import { UIUpdater } from '../components/uiUpdater.js';

/**
 * @typedef {object} ActivoBilletera
 * @property {string} ticker - El símbolo de la criptomoneda (ej. 'BTC').
 * @property {string} nombre - El nombre completo de la criptomoneda (ej. 'Bitcoin').
 * @property {string} logo - La URL del logo de la criptomoneda.
 * @property {boolean} es_polvo - `true` si la cantidad del activo es considerada insignificante ("polvo").
 * @property {string} ganancia_perdida_cruda - El valor numérico de la ganancia/pérdida, sin formato.
 * @property {string} cantidad_total_formatted - La cantidad total del activo, formateada para mostrar.
 * @property {string} cantidad_disponible_formatted - La cantidad disponible (no en órdenes), formateada.
 * @property {string} cantidad_reservada_formatted - La cantidad reservada en órdenes abiertas, formateada.
 * @property {string} cantidad_reservada - El valor numérico de la cantidad reservada.
 * @property {string} precio_actual_formatted - El precio de mercado actual, formateado.
 * @property {string} valor_usdt_formatted - El valor total del activo en USDT, formateado.
 * @property {string} ganancia_perdida_formatted - La ganancia o pérdida total, formateada.
 * @property {string} porcentaje_ganancia_formatted - El porcentaje de ganancia/pérdida, formateado.
 * @property {string} porcentaje_formatted - El porcentaje que este activo representa en la billetera, formateado.
 */

/**
 * @private
 * @function createBilleteraRowHTML
 * @description Función pura de template. Genera una fila HTML (`<tr>`) para un activo en la tabla de la billetera.
 * @param {ActivoBilletera} cripto - El objeto que contiene los datos del activo a renderizar.
 * @returns {string} Una cadena de texto con el HTML de la fila de la tabla.
 */
function createBilleteraRowHTML(cripto) {
    const colorGanancia = parseFloat(cripto.ganancia_perdida_cruda) >= 0 ? 'text-success' : 'text-danger';
    const claseFila = cripto.es_polvo ? 'fila-polvo' : '';
    const reservadoClase = parseFloat(cripto.cantidad_reservada) > 0 ? 'text-warning' : '';

    return `
        <tr class="${claseFila}">
            <td class="text-start ps-3">
                <img src="${cripto.logo}" width="24" class="me-3" style="vertical-align: middle;" alt="${cripto.ticker} logo">
                <span class="fw-bold fs-6">${cripto.nombre}</span>
                <span class="text-white-50 ms-2">(${cripto.ticker})</span>
            </td>
            <td class="text-end pe-3">${cripto.cantidad_total_formatted}</td>
            <td class="text-end pe-3">${cripto.cantidad_disponible_formatted}</td>
            <td class="text-end pe-3 ${reservadoClase}">${cripto.cantidad_reservada_formatted}</td>
            <td class="text-end pe-3">${cripto.precio_actual_formatted}</td>
            <td class="text-end pe-3 fw-bold">${cripto.valor_usdt_formatted}</td>
            <td class="text-end pe-3 ${colorGanancia}">${cripto.ganancia_perdida_formatted}</td>
            <td class="text-end pe-3 ${colorGanancia}">${cripto.porcentaje_ganancia_formatted}</td>
            <td class="text-end pe-3">${cripto.porcentaje_formatted}</td>
        </tr>
    `;
}

/**
 * @private
 * @description Obtiene los datos de la billetera desde la API y los renderiza en la tabla principal.
 * Maneja los estados de carga, éxito (con o sin datos) y error.
 * @effects Modifica el `innerHTML` del `<tbody>` de la tabla `#tabla-billetera`.
 */
async function renderBilletera() {
    const cuerpoTabla = document.getElementById('tabla-billetera');
    if (!cuerpoTabla) return;

    try {
        const datosBilletera = await fetchEstadoBilletera();
        if (!datosBilletera || datosBilletera.length === 0) {
            cuerpoTabla.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">Tu billetera está vacía.</td></tr>';
        } else {
            cuerpoTabla.innerHTML = datosBilletera.map(createBilleteraRowHTML).join('');
        }
    } catch (error) {
        console.error('Error al renderizar la billetera:', error);
        UIUpdater.mostrarMensajeError('No se pudieron cargar los datos de la billetera.');
        cuerpoTabla.innerHTML = '<tr><td colspan="9" class="text-center text-danger py-4">Error al cargar los datos.</td></tr>';
    }
}

/**
 * @private
 * @function createComisionRowHTML
 * @description Función pura de template. Genera una fila HTML para la tabla de historial de comisiones.
 * @param {object} comision - El objeto de datos de la comisión.
 * @returns {string} Una cadena de texto con el HTML de la fila.
 */
function createComisionRowHTML(comision) {
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
 * @private
 * @description Obtiene el historial de comisiones desde la API y lo renderiza en su tabla.
 * @effects Modifica el `innerHTML` del `<tbody>` de la tabla `#tabla-comisiones`.
 */
async function renderComisiones() {
    const cuerpoTabla = document.getElementById('tabla-comisiones');
    if (!cuerpoTabla) return;

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
 * @private
 * @description Configura el listener para el interruptor que oculta o muestra los activos "polvo".
 * @effects Añade un listener de evento 'change' al elemento `#ocultar-polvo-switch`.
 */
function setupEventListeners() {
    const switchOcultarPolvo = document.getElementById('ocultar-polvo-switch');
    if (switchOcultarPolvo) {
        switchOcultarPolvo.addEventListener('change', (event) => {
            const filasPolvo = document.querySelectorAll('.fila-polvo');
            const estaActivado = event.target.checked;
            
            filasPolvo.forEach(fila => {
                fila.style.display = estaActivado ? 'none' : 'table-row';
            });
        });
    }
}

/**
 * @description Punto de entrada principal del script. Se ejecuta cuando el DOM está completamente cargado.
 * Inicia el renderizado de las tablas y, una vez completado, configura los listeners de eventos.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Promise.all asegura que ambas operaciones de renderizado se inicien en paralelo.
    Promise.all([
        renderBilletera(),
        renderComisiones()
    ]).finally(() => {
        // .finally() asegura que los listeners se configuren independientemente de si las promesas tuvieron éxito o no.
        // Esto es importante para que el switch de "ocultar polvo" funcione incluso si una de las tablas falló en cargar.
        setupEventListeners();
    });
});