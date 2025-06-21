// Este es el punto de entrada para la página de cotizaciones (index.html).
import { triggerActualizacionDatos } from './cotizacionesApiService.js';
import { renderTabla } from './tablaCotizacionesUI.js';

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

/**
 * Función principal que se ejecuta al cargar la página.
 */
function main() {
    // Asegurarse de que estamos en la página correcta verificando la existencia de la tabla.
    if (document.getElementById('tabla-datos')) {
        console.log("🚀 Inicializando página de cotizaciones.");
        
        // Carga inicial de la tabla
        renderTabla();
        
        // Inicia el ciclo de actualización automática
        inicializarActualizadorAutomatico();
    }
}

// Ejecutar la función principal
main();