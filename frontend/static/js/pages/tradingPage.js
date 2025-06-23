/**
 * @module pages/tradingPage
 * @description Orquesta toda la lógica de la página de trading. Se encarga de la inicialización,
 * la gestión del estado, la interacción del usuario y la comunicación con otros módulos
 * como el gráfico, el formulario y los servicios de API.
 */

import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart, updateChartData } from '../components/chartRenderer.js';
import { fetchCotizaciones, fetchEstadoBilletera, fetchHistorial, fetchVelas } from '../services/apiService.js';
import { AppState } from '../services/appState.js';
// Esta importación ahora funcionará porque el archivo existe en la ruta correcta.
import { saveTradingState, loadTradingState } from '../services/statePersistence.js';

document.addEventListener('DOMContentLoaded', () => {
    let currentTicker;
    let currentInterval;
    let isChartLoading = false;

    function setTradeMode(mode, defaultTicker) {
        DOMElements.inputAccion.val(mode);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();

        let tickerForBalance = '';
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();

        if (UIState.esModoCompra()) {
            const cryptosWithoutUSDT = allCryptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, cryptosWithoutUSDT, defaultTicker);
            tickerForBalance = UIState.getTickerPago();
        } else {
            if (!ownedCoins || ownedCoins.length === 0) {
                console.warn("No se encontraron monedas en propiedad para configurar el modo de venta.");
                FormLogic.popularSelector(DOMElements.selectorPrincipal, [], null);
                tickerForBalance = null;
            } else {
                const validDefault = ownedCoins.some(c => c.ticker === defaultTicker) ? defaultTicker : ownedCoins[0].ticker;
                tickerForBalance = FormLogic.popularSelector(DOMElements.selectorPrincipal, ownedCoins, validDefault);
            }
        }

        UIUpdater.mostrarSaldo(tickerForBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    async function actualizarGrafico(ticker, interval) {
        if (isChartLoading) {
            console.log("Petición de actualización de gráfico ignorada: carga en curso.");
            return;
        }
        isChartLoading = true;
        console.log(`Solicitando datos de velas para ${ticker} en intervalo ${interval}...`);
        try {
            const nuevosDatosVelas = await fetchVelas(ticker, interval);
            updateChartData(nuevosDatosVelas);
        } catch (error) {
            console.error(`Error al actualizar el gráfico para ${ticker}/${interval}:`, error);
            updateChartData([]);
        } finally {
            isChartLoading = false;
        }
    }

    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar', currentTicker));
        DOMElements.botonVender.on('click', () => setTradeMode('vender', currentTicker));

        DOMElements.selectorPrincipal.on('change', () => {
            currentTicker = UIState.getTickerPrincipal();
            UIUpdater.actualizarLabelMonto();
            if (!UIState.esModoCompra()) {
                UIUpdater.mostrarSaldo(currentTicker);
            }
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });

        $('#timeframe-selector').on('click', '.timeframe-btn', function() {
            const $btn = $(this);
            if ($btn.hasClass('active')) return;
            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $btn.addClass('active');
            currentInterval = $btn.data('interval');
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });

        DOMElements.selectorPagarCon.on('change', () => {
            UIUpdater.actualizarLabelMonto();
            if (UIState.esModoCompra()) UIUpdater.mostrarSaldo(UIState.getTickerPago());
        });

        DOMElements.selectorRecibirEn.on('change', UIUpdater.actualizarLabelMonto);
        DOMElements.radioModoIngreso.on('change', UIUpdater.actualizarLabelMonto);

        DOMElements.sliderMonto.on('input', () => {
            const calculatedValue = FormLogic.calcularMontoSlider();
            UIUpdater.setInputMonto(calculatedValue.toFixed(8));
        });
    }

    async function initialize() {
        console.log("Inicializando página de trading...");
        
        const savedState = loadTradingState();
        currentTicker = savedState?.ticker || 'BTC';
        currentInterval = savedState?.interval || '1d';
        console.log(`Estado cargado: Ticker=${currentTicker}, Intervalo=${currentInterval}`);

        try {
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval)
            ]);

            AppState.setAllCryptos(cotizaciones);
            const ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.cantidad) > 0);
            AppState.setOwnedCoins(ownedCoins);
            
            UIUpdater.renderHistorial(historial);
            initializeChart(velas);

            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({
                    width: '100%',
                    dropdownCssClass: 'text-dark',
                    theme: "bootstrap-5"
                });
            });

            FormLogic.popularSelector(DOMElements.selectorPagarCon, AppState.getOwnedCoins(), 'USDT');
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, AppState.getAllCryptos().filter(c => c.ticker !== 'USDT'), 'USDT');

            setupEventListeners();
            setTradeMode('comprar', currentTicker);
            
            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $(`#timeframe-selector .timeframe-btn[data-interval="${currentInterval}"]`).addClass('active');

            console.log("Página de trading inicializada correctamente.");
        } catch (error) {
            console.error('Error fatal durante la inicialización de la página de trading:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales. Por favor, recarga la página.');
        }
    }

    initialize();
});