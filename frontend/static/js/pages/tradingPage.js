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
 */
async function initialize() {
    // 1. Determinar el estado inicial (ticker e intervalo) desde la URL o el almacenamiento local.
    const urlParams = new URLSearchParams(window.location.search);
    const tickerDesdeUrl = urlParams.get('ticker');
    const savedState = loadTradingState();
    const initialTicker = tickerDesdeUrl || savedState?.ticker || 'BTC';
    const initialInterval = savedState?.interval || '1d';

    // Si se especificó un ticker en la URL, se guarda como el nuevo estado por defecto.
    if (tickerDesdeUrl) {
        saveTradingState(initialTicker, initialInterval);
    }

    try {
        // 2. Cargar los datos esenciales del backend antes de renderizar nada.
        await triggerActualizacionDatos();
        const { historial, ordenesAbiertas } = await AppDataManager.loadInitialData();

        // 3. Inicializar los componentes de la UI una sola vez.
        // Esto prepara el terreno pero no necesariamente carga todos los datos visuales.
        UIManager.initialize({
            ticker: initialTicker,
            interval: initialInterval,
            historial,
            ordenesAbiertas,
        });
        
        // 4. Inicializar el gráfico con un estado vacío para que la UI no se rompa.
        initializeChart([]);

        // 5. Aplicar cualquier estado de formulario guardado después de un envío.
        UIManager.applyFormStateFromStorage();
        
        // 6. Cargar los datos del gráfico (que pueden tardar) de forma asíncrona.
        fetchVelas(initialTicker, initialInterval)
            .then(datosVelas => {
                updateChartData(datosVelas); // Actualiza el gráfico cuando los datos lleguen.
            })
            .catch(err => {
                console.error("Error al cargar datos del gráfico:", err);
                updateChartData([]); // Muestra el mensaje de error en el gráfico.
            });

        // 7. Iniciar el sondeo periódico para mantener la página actualizada.
        setInterval(async () => {
            const data = await AppDataManager.pollData();
            if (data) {
                // Actualiza solo las partes que cambian, como las órdenes y el saldo.
                UIManager.renderOrdenesAbiertas(data.nuevasOrdenesAbiertas);
                UIManager.updateDynamicLabels();
            }
        }, POLLING_INTERVAL_MS);

    } catch (error) {
        // Manejo de errores críticos durante la carga inicial.
        console.error('Error crítico durante la inicialización de la página de trading:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error de Conexión',
            text: 'No se pudieron cargar los datos esenciales. Por favor, recarga la página.',
            background: '#212529',
            color: '#f8f9fa',
            confirmButtonColor: '#0d6efd',
        });
    }
}

/**
 * Punto de entrada del script. Dispara la función de inicialización
 * una vez que el contenido del DOM está completamente cargado y listo.
 * @event DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', initialize);  