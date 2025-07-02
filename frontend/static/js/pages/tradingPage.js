// frontend/static/js/pages/tradingPage.js

import { AppDataManager } from '../services/appDataManager.js';
import { UIManager } from '../components/uiManager.js';
import { initializeChart, updateChartData } from '../components/chartRenderer.js';
import { loadTradingState, saveTradingState } from '../services/statePersistence.js';
import { fetchVelas } from '../services/apiService.js';

const POLLING_INTERVAL_MS = 20000; // 20 segundos

/**
 * Función principal que orquesta la inicialización de la página.
 */
async function initialize() {
    console.log('Inicializando página de trading...');

    const urlParams = new URLSearchParams(window.location.search);
    const tickerDesdeUrl = urlParams.get('ticker');
    const savedState = loadTradingState();
    const initialTicker = tickerDesdeUrl || savedState?.ticker || 'BTC';
    const initialInterval = savedState?.interval || '1d';
    if (tickerDesdeUrl) saveTradingState(initialTicker, initialInterval);

    try {
        const { historial, ordenesAbiertas } = await AppDataManager.loadInitialData();
        
        UIManager.initialize({
            ticker: initialTicker,
            interval: initialInterval,
            historial,
            ordenesAbiertas
        });
        
        const datosVelas = await fetchVelas(initialTicker, initialInterval);
        initializeChart(datosVelas);
        
        UIManager.setupEventListeners();

        setInterval(async () => {
            const data = await AppDataManager.pollData();
            if (data) {
                UIManager.renderOrdenesAbiertas(data.nuevasOrdenesAbiertas);
                UIManager.updateDynamicLabels();
            }
        }, POLLING_INTERVAL_MS);

        console.log('Página de trading inicializada correctamente.');

    } catch (error) {
        Swal.fire({
            icon: 'error', title: 'Error de Conexión',
            text: 'No se pudieron cargar los datos esenciales. Por favor, recarga la página.',
            background: '#212529', color: '#f8f9fa'
        });
    }
}

// Punto de entrada
document.addEventListener('DOMContentLoaded', initialize);