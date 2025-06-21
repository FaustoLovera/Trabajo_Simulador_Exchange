/**
 * @module pages/indexPage
 * @description Lógica para la página principal de cotizaciones.
 * Se encarga de inicializar y gestionar la actualización periódica de la tabla de cotizaciones.
 */

import { triggerActualizacionDatos } from '../services/apiService.js';
import { renderTabla } from '../components/tablaCotizacionesUI.js';

/**
 * @const {number} UPDATE_INTERVAL_MS
 * @description Intervalo en milisegundos para la actualización automática de la tabla de cotizaciones.
 * @default 15000
 */
const UPDATE_INTERVAL_MS = 15000; // 15 segundos

/**
 * Orquesta el ciclo completo de actualización de datos y renderizado de la tabla.
 * Primero, solicita al backend que actualice sus datos desde la fuente externa.
 * Una vez completado, renderiza la tabla de cotizaciones con la información más reciente.
 * @async
 * @function actualizarYRenderizar
 * @throws {Error} Si alguna de las operaciones (actualización o renderizado) falla.
 */
async function actualizarYRenderizar() {
    console.log("Iniciando ciclo de actualización de cotizaciones...");
    try {
        await triggerActualizacionDatos();
        await renderTabla();
        console.log("Tabla de cotizaciones actualizada exitosamente.");
    } catch (error) {
        console.error("Falló el ciclo de actualización de la tabla de cotizaciones:", error);
    }
}

/**
 * @description Listener que se ejecuta cuando el DOM está completamente cargado.
 * Verifica si la tabla de cotizaciones existe en la página actual y, si es así,
 * inicia el ciclo de actualización inmediata y periódica.
 * @event DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Asegurarse de que el script solo se ejecute en la página correcta.
    if (document.getElementById('tabla-datos')) {
        console.log("Página de cotizaciones detectada. Iniciando actualizaciones.");
        
        // Ejecuta la actualización inmediatamente al cargar la página.
        actualizarYRenderizar();
        
        // Establece el intervalo para futuras actualizaciones automáticas.
        setInterval(actualizarYRenderizar, UPDATE_INTERVAL_MS);
    }
});