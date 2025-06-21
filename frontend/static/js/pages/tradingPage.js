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

document.addEventListener('DOMContentLoaded', () => {
    /** @type {string} El ticker de la criptomoneda actualmente seleccionada en el gráfico. */
    let currentTicker = 'BTC';
    /** @type {string} La temporalidad (intervalo) actual del gráfico (ej. '1d', '1h'). */
    let currentInterval = '1d';
    /** @type {boolean} Bandera para prevenir cargas concurrentes de datos para el gráfico. */
    let isChartLoading = false;

    /**
     * Configura la interfaz de usuario para el modo de operación especificado (compra o venta).
     * @param {'comprar' | 'vender'} mode - El modo de trading a activar.
     */
    function setTradeMode(mode) {
        DOMElements.inputAccion.val(mode);

        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();

        let tickerForBalance = '';
        if (UIState.esModoCompra()) {
            // En modo COMPRA, el selector principal muestra todas las criptos disponibles para comprar.
            const cryptosWithoutUSDT = window.allCryptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, cryptosWithoutUSDT, 'BTC');
            // El saldo a mostrar es el de la moneda con la que se paga (ej. USDT).
            tickerForBalance = UIState.getTickerPago();
        } else {
            // En modo VENTA, el selector principal muestra solo las criptos que el usuario posee.
            if (!window.ownedCoins || window.ownedCoins.length === 0) {
                console.warn("No se encontraron monedas en propiedad para configurar el modo de venta.");
                tickerForBalance = null; // No se puede mostrar saldo si no hay monedas.
            } else {
                const defaultTicker = window.ownedCoins[0].ticker;
                tickerForBalance = FormLogic.popularSelector(DOMElements.selectorPrincipal, window.ownedCoins, defaultTicker);
            }
        }

        UIUpdater.mostrarSaldo(tickerForBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    /**
     * Obtiene los datos de velas para un par y temporalidad específicos y actualiza el gráfico.
     * Utiliza una bandera (`isChartLoading`) para evitar peticiones concurrentes.
     * @async
     * @param {string} ticker - El ticker de la criptomoneda (ej. 'BTC').
     * @param {string} interval - La temporalidad del gráfico (ej. '1d', '15m').
     */
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
            updateChartData([]); // En caso de error, limpia el gráfico y muestra un mensaje.
        } finally {
            isChartLoading = false; // Restablece la bandera para permitir futuras peticiones.
        }
    }

    /**
     * Configura todos los manejadores de eventos para los elementos interactivos de la página.
     */
    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        DOMElements.selectorPrincipal.on('change', () => {
            currentTicker = UIState.getTickerPrincipal();
            UIUpdater.actualizarLabelMonto();
            if (!UIState.esModoCompra()) {
                UIUpdater.mostrarSaldo(currentTicker);
            }
            actualizarGrafico(currentTicker, currentInterval);
        });

        // Delega el evento de clic para los botones de temporalidad.
        $('#timeframe-selector').on('click', '.timeframe-btn', function() {
            const $btn = $(this);
            if ($btn.hasClass('active')) return;

            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $btn.addClass('active');

            currentInterval = $btn.data('interval');
            actualizarGrafico(currentTicker, currentInterval);
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

    /**
     * Función principal que inicializa la página de trading.
     * Carga datos críticos en paralelo, renderiza componentes y configura los listeners.
     * @async
     */
    async function initialize() {
        console.log("Inicializando página de trading...");
        try {
            // Carga todos los datos necesarios de forma concurrente para optimizar el tiempo de carga.
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval) // Carga inicial para BTC en 1D.
            ]);

            // Almacena los datos en el objeto `window` para acceso global dentro de la página.
            window.allCryptos = cotizaciones;
            window.ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.cantidad) > 0);

            // Renderiza los componentes que dependen de los datos cargados.
            UIUpdater.renderHistorial(historial);
            initializeChart(velas);

            // Inicializa la biblioteca Select2 en los selectores para mejorar su apariencia y funcionalidad.
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({
                    width: '100%',
                    dropdownCssClass: 'text-dark',
                    theme: "bootstrap-5"
                });
            });

            // Popula los selectores con las opciones correspondientes.
            FormLogic.popularSelector(DOMElements.selectorPagarCon, window.ownedCoins, 'USDT');
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.allCryptos, 'USDT');

            setupEventListeners();
            
            // Establece el estado inicial de la UI en modo 'comprar'.
            setTradeMode('comprar');
            
            // Marca visualmente la temporalidad '1d' como activa.
            $('#timeframe-selector .timeframe-btn[data-interval="1d"]').addClass('active');

            console.log("Página de trading inicializada correctamente.");
        } catch (error) {
            console.error('Error fatal durante la inicialización de la página de trading:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales. Por favor, recarga la página.');
        }
    }

    // Inicia todo el proceso de inicialización.
    initialize();
});