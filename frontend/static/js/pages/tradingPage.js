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
import { saveTradingState, loadTradingState } from '../services/statePersistence.js';

document.addEventListener('DOMContentLoaded', () => {
    let currentTicker;
    let currentInterval;
    let isChartLoading = false;

    function actualizarFormularioUI() {
        const esCompra = UIState.esModoCompra();
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();

        if (esCompra) {
            const listaParaComprar = allCryptos.filter((c) => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, listaParaComprar, currentTicker);
        } else {
            FormLogic.popularSelector(
                DOMElements.selectorPrincipal,
                ownedCoins,
                currentTicker,
                'No tienes monedas para vender'
            );
        }

        FormLogic.actualizarOpcionesDeSelectores();

        const tickerParaBalance = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        UIUpdater.mostrarSaldo(tickerParaBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    function setTradeMode(mode) {
        DOMElements.inputAccion.val(mode);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
        actualizarFormularioUI();
    }

    async function actualizarGrafico(ticker, interval) {
        if (!ticker || isChartLoading) {
            if (!ticker) console.warn('Intento de actualizar gráfico sin ticker seleccionado.');
            if (isChartLoading) console.log('Petición de actualización de gráfico ignorada: carga en curso.');
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
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        DOMElements.selectorPrincipal.on('change', () => {
            const nuevoTicker = UIState.getTickerPrincipal();
            if (!nuevoTicker || nuevoTicker === currentTicker) return;

            currentTicker = nuevoTicker;
            FormLogic.actualizarOpcionesDeSelectores();
            UIUpdater.actualizarLabelMonto();
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });

        DOMElements.selectorPagarCon.on('change', () => {
            UIUpdater.mostrarSaldo(UIState.getTickerPago());
            UIUpdater.actualizarLabelMonto();
        });
        DOMElements.selectorRecibirEn.on('change', UIUpdater.actualizarLabelMonto);

        $('#timeframe-selector').on('click', '.timeframe-btn', function () {
            const $btn = $(this);
            if ($btn.hasClass('active')) return;
            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $btn.addClass('active');
            currentInterval = $btn.data('interval');
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });

        DOMElements.radioModoIngreso.on('change', UIUpdater.actualizarLabelMonto);

        DOMElements.sliderMonto.on('input', () => {
            const calculatedValue = FormLogic.calcularMontoSlider();
            UIUpdater.setInputMonto(calculatedValue.toFixed(8));
        });
    }

    async function initialize() {
        console.log('Inicializando página de trading...');

        const urlParams = new URLSearchParams(window.location.search);
        const tickerDesdeUrl = urlParams.get('ticker');
        const savedState = loadTradingState();

        currentTicker = tickerDesdeUrl || savedState?.ticker || 'BTC';
        currentInterval = savedState?.interval || '1d';

        if (tickerDesdeUrl) {
            saveTradingState(currentTicker, currentInterval);
        }
        console.log(`Estado inicial decidido: Ticker=${currentTicker}, Intervalo=${currentInterval}`);

        try {
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval),
            ]);

            AppState.setAllCryptos(cotizaciones);
            const ownedCoins = estadoBilletera.filter((moneda) => parseFloat(moneda.cantidad) > 0);
            AppState.setOwnedCoins(ownedCoins);

            UIUpdater.renderHistorial(historial);
            initializeChart(velas);

            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(
                (sel) => {
                    sel.select2({
                        width: '100%',
                        dropdownCssClass: 'text-dark',
                        theme: 'bootstrap-5',
                    });
                }
            );

            setupEventListeners();
            setTradeMode('comprar');

            DOMElements.selectorPrincipal.val(currentTicker).trigger('change');

            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $(`#timeframe-selector .timeframe-btn[data-interval="${currentInterval}"]`).addClass('active');

            console.log('Página de trading inicializada correctamente.');
        } catch (error) {
            console.error('Error fatal durante la inicialización de la página de trading:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales. Por favor, recarga la página.');
        }
    }

    initialize();
});
