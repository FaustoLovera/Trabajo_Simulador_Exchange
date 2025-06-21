// Orquesta la inicialización y la lógica principal de la página de inicio (listado de cotizaciones).
import { triggerActualizacionDatos } from '../services/apiService.js';
import { renderTabla } from '../components/tablaCotizacionesUI.js';

const UPDATE_INTERVAL_MS = 15000; // 15 segundos

/**
 * Configura la actualización automática de la tabla de cotizaciones.
 */
function inicializarActualizadorAutomatico() {
    setInterval(async () => {
        console.log("⏳ Solicitando actualización de datos...");
        await triggerActualizacionDatos();
        await renderTabla();
    }, UPDATE_INTERVAL_MS);
}

document.addEventListener('DOMContentLoaded', () => {
    // Asegurarse de que estamos en la página correcta verificando la existencia de la tabla.
    if (document.getElementById('tabla-datos')) {
        console.log("🚀 Inicializando página de cotizaciones.");
        
        // Carga inicial de la tabla
        renderTabla();
        
        // Inicia el ciclo de actualización automática
        inicializarActualizadorAutomatico();
    }
});