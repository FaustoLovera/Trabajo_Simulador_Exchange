// frontend/static/js/pages/tradingPage.js
import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart, updateChartData } from '../components/chartRenderer.js';
import { fetchCotizaciones, fetchEstadoBilletera, fetchHistorial, fetchVelas } from '../services/apiService.js';

document.addEventListener('DOMContentLoaded', () => {
    // Variables para mantener el estado actual del gráfico
    let currentTicker = 'BTC';
    let currentInterval = '1d';

    // Variable para evitar llamadas múltiples mientras se carga una.
    let isChartLoading = false;

    // --- (función setTradeMode sin cambios) ---
    function setTradeMode(mode) {
        DOMElements.inputAccion.val(mode);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
        let tickerForBalance = '';
        if (UIState.esModoCompra()) {
            const cryptosWithoutUSDT = window.allCryptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, cryptosWithoutUSDT, 'BTC');
            tickerForBalance = UIState.getTickerPago();
        } else {
            const defaultTicker = window.ownedCoins.length > 0 ? window.ownedCoins[0].ticker : null;
            tickerForBalance = FormLogic.popularSelector(DOMElements.selectorPrincipal, window.ownedCoins, defaultTicker);
        }
        UIUpdater.mostrarSaldo(tickerForBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }
    // --- (fin de setTradeMode) ---
    
    /**
     * Función centralizada para obtener datos de velas y actualizar el gráfico.
     * @param {string} ticker El ticker de la criptomoneda.
     * @param {string} interval La temporalidad del gráfico.
     */
    async function actualizarGrafico(ticker, interval) {
        if (isChartLoading) {
            console.log("Ignorando petición de gráfico, ya hay una en curso.");
            return;
        }
        isChartLoading = true;
        try {
            console.log(`📈 Pidiendo velas para ${ticker} en ${interval}...`);
            const nuevosDatosVelas = await fetchVelas(ticker, interval);
            updateChartData(nuevosDatosVelas);
        } catch (error) {
            console.error(`❌ Error al actualizar el gráfico para ${ticker}/${interval}:`, error);
            updateChartData([]); // Muestra el overlay de error
        } finally {
            isChartLoading = false; // Permite nuevas peticiones
        }
    }

    /**
     * Configura todos los event listeners de la página.
     */
    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        // Listener del selector principal de criptomoneda
        DOMElements.selectorPrincipal.on('change', () => {
            currentTicker = UIState.getTickerPrincipal();
            UIUpdater.actualizarLabelMonto();
            if (!UIState.esModoCompra()) {
                UIUpdater.mostrarSaldo(currentTicker);
            }
            actualizarGrafico(currentTicker, currentInterval);
        });

        // Listener para los botones de temporalidad
        $('#timeframe-selector').on('click', '.timeframe-btn', function() {
            const $btn = $(this);
            if ($btn.hasClass('active')) return;

            $('.timeframe-btn').removeClass('active');
            $btn.addClass('active');

            currentInterval = $btn.data('interval');
            actualizarGrafico(currentTicker, currentInterval);
        });

        // Listeners del formulario que no afectan al gráfico
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

    /**
     * Función principal de inicialización.
     */
    async function initialize() {
        try {
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval) // Carga inicial con las variables de estado
            ]);
            
            window.allCryptos = cotizaciones;
            window.ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.cantidad) > 0);
            
            UIUpdater.renderHistorial(historial);
            initializeChart(velas);
            
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({ 
                    width: '100%', 
                    dropdownCssClass: 'text-dark',
                    theme: 'bootstrap-5'
                });
            });

            FormLogic.popularSelector(DOMElements.selectorPagarCon, window.ownedCoins, 'USDT');
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.allCryptos, 'USDT');
            
            setupEventListeners();
            setTradeMode('comprar');
            // Asegurarse de que el botón '1D' esté activo visualmente en la carga inicial
            $('#timeframe-selector .timeframe-btn[data-interval="1d"]').addClass('active');


        } catch (error) {
            console.error('Error fatal durante la inicialización:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales para la página de trading.');
        }
    }

    initialize();
});