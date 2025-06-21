// frontend/static/js/pages/indexPage.js

import { triggerActualizacionDatos } from '../services/apiService.js';
import { renderTabla } from '../components/tablaCotizacionesUI.js';

const UPDATE_INTERVAL_MS = 15000; // 15 segundos

/**
 * Función unificada para actualizar datos y renderizar la tabla.
 */
async function actualizarYRenderizar() {
    console.log("🔄 Actualizando y renderizando cotizaciones...");
    try {
        // Primero, le pedimos al backend que se actualice desde la API externa.
        await triggerActualizacionDatos();
        // Luego, renderizamos la tabla con los datos frescos.
        await renderTabla();
        console.log("✅ Tabla de cotizaciones actualizada.");
    } catch (error) {
        console.error("❌ Falló el ciclo de actualización:", error);
        // Opcional: podrías mostrar un mensaje de error en la UI aquí.
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('tabla-datos')) {
        console.log("🚀 Inicializando página de cotizaciones.");
        
        // 1. Ejecuta la actualización INMEDIATAMENTE al cargar la página.
        actualizarYRenderizar();
        
        // 2. Luego, establece el intervalo para futuras actualizaciones.
        setInterval(actualizarYRenderizar, UPDATE_INTERVAL_MS);
    }
});