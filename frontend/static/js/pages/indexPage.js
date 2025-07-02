/**
 * @file Controlador para la página principal de cotizaciones (`index.html`).
 * @module pages/indexPage
 * @description Este script gestiona la lógica de la página de inicio, cuya principal
 * responsabilidad es mostrar una tabla de cotizaciones de mercado actualizada periódicamente.
 */

import { triggerActualizacionDatos } from '../services/apiService.js';
import { renderTabla } from '../components/tablaCotizacionesUI.js';

/**
 * Intervalo en milisegundos para la actualización automática de la tabla de cotizaciones.
 * @private
 * @const {number}
 * @default 15000
 */
const UPDATE_INTERVAL_MS = 15000; // 15 segundos

/**
 * @private
 * @async
 * @function actualizarYRenderizar
 * @description Orquesta el ciclo completo de actualización y renderizado.
 * 1. Solicita al backend que actualice sus datos de mercado desde la API externa.
 * 2. Una vez que el backend confirma la actualización, renderiza la tabla en el frontend
 *    con los datos más recientes obtenidos del servidor.
 * @effects Llama a `renderTabla`, que modifica el DOM para actualizar la tabla de cotizaciones.
 * @throws {Error} Si alguna de las operaciones (actualización o renderizado) falla, el error
 * se captura y se registra en la consola sin detener el ciclo periódico.
 */
async function actualizarYRenderizar() {
    try {
        // Paso 1: Indicar al backend que actualice sus datos internos.
        await triggerActualizacionDatos();
        // Paso 2: Renderizar la tabla con los datos ya actualizados en el backend.
        await renderTabla();
    } catch (error) {
        console.error("Falló el ciclo de actualización de la tabla de cotizaciones:", error);
        // Nota: No se muestra un mensaje de error al usuario para no ser intrusivo,
        // ya que la tabla simplemente no se actualizará en este ciclo.
    }
}

/**
 * Punto de entrada del script. Se ejecuta cuando el DOM está completamente cargado.
 * Verifica si la tabla de cotizaciones existe en la página y, de ser así, inicia el ciclo
 * de actualización: una vez de inmediato y luego periódicamente.
 * @event DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Confirma que estamos en la página correcta antes de ejecutar la lógica.
    if (document.getElementById('tabla-datos')) {
        // Ejecuta la actualización inmediatamente al cargar la página para mostrar datos frescos.
        actualizarYRenderizar();
        
        // Establece el intervalo para futuras actualizaciones automáticas.
        setInterval(actualizarYRenderizar, UPDATE_INTERVAL_MS);
    }
});