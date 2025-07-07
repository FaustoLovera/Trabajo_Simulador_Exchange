/**
 * @file Orquestador principal y punto de entrada para la página de trading (`trading.html`).
 * @module pages/tradingPage
 * @description Este script es el corazón de la página de trading. Se encarga de inicializar todos
 * los componentes de la interfaz, cargar los datos iniciales (historial, órdenes), renderizar el
 * gráfico de velas, y establecer un ciclo de sondeo para mantener los datos dinámicos actualizados.
 */

import { AppDataManager } from '../services/appDataManager.js';
import { UIManager } from '../components/uiManager.js';
import { initializeChart, updateChartData } from '../components/chartRenderer.js';
import { loadTradingState, saveTradingState } from '../services/statePersistence.js';
import { fetchVelas, triggerActualizacionDatos } from '../services/apiService.js';

/**
 * Intervalo en milisegundos para el sondeo periódico de datos dinámicos como órdenes abiertas.
 * @private
 * @const {number}
 */
const POLLING_INTERVAL_MS = 15000; // 15 segundos

/**
 * @private
 * @async
 * @function initialize
 * @description Orquesta la secuencia de inicialización completa de la página de trading.
 * 1. Determina el ticker y el intervalo a mostrar (desde URL o estado guardado).
 * 2. Carga datos esenciales (historial, órdenes) a través de `AppDataManager`.
 * 3. Inicializa el `UIManager` con los datos y el estado inicial.
 * 4. Obtiene los datos de velas y renderiza el gráfico principal.
 * 5. Configura todos los manejadores de eventos de la UI.
 * 6. Inicia un sondeo periódico para actualizar datos en tiempo real (órdenes, saldos).
 * @effects Modifica gran parte del DOM a través de `UIManager` y `initializeChart`.
 *          Muestra una alerta de error si la carga inicial falla.
 */
async function initialize() {
    const urlParams = new URLSearchParams(window.location.search);
    const tickerDesdeUrl = urlParams.get('ticker');
    const savedState = loadTradingState();
    const initialTicker = tickerDesdeUrl || savedState?.ticker || 'BTC';
    const initialInterval = savedState?.interval || '1d';
    if (tickerDesdeUrl) saveTradingState(initialTicker, initialInterval);

    try {
        // 1. Carga los datos esenciales (rápidos)
        await triggerActualizacionDatos(); // Buena práctica añadir esto aquí
        const { historial, ordenesAbiertas } = await AppDataManager.loadInitialData();

        // 2. Inicializa la UI, el gráfico (vacío) y los listeners INMEDIATAMENTE
        UIManager.initialize({
            ticker: initialTicker,
            interval: initialInterval,
            historial,
            ordenesAbiertas
        });
        
        // Inicializa la UI, el gráfico (vacío) y los listeners INMEDIATAMENTE
        UIManager.initialize({
            ticker: initialTicker,
            interval: initialInterval,
            historial,
            ordenesAbiertas
        });
        
        UIManager.applyFormStateFromStorage(); // Aplicar el estado guardado al formulario

        initializeChart([]); // <-- Inicializa el gráfico vacío para que no falle.
        
        // 3. Carga los datos pesados del gráfico de forma asíncrona SIN bloquear
        fetchVelas(initialTicker, initialInterval)
            .then(datosVelas => {
                updateChartData(datosVelas); // Actualiza el gráfico cuando los datos lleguen
            })
            .catch(err => {
                console.error("Error al cargar datos del gráfico:", err);
                updateChartData([]); // Muestra el mensaje de error en el gráfico
            });

        // 4. Inicia el sondeo periódico (polling)
        setInterval(async () => {
            const data = await AppDataManager.pollData();
            if (data) {
                UIManager.renderOrdenesAbiertas(data.nuevasOrdenesAbiertas);
                UIManager.updateDynamicLabels();
            }
        }, POLLING_INTERVAL_MS);

    } catch (error) {
        console.error('Error crítico durante la inicialización de la página de trading:', error);
        Swal.fire({
            icon: 'error', title: 'Error de Conexión',
            text: 'No se pudieron cargar los datos esenciales. Por favor, recarga la página.',
            background: '#212529', color: '#f8f9fa',
            confirmButtonColor: '#0d6efd'
        });
    }
}

/**
 * Punto de entrada del script. Dispara la función de inicialización
 * una vez que el contenido del DOM está completamente cargado y listo.
 * @event DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', initialize);