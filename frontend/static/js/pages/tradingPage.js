// frontend/static/js/pages/tradingPage.js
import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart, updateChartData } from '../components/chartRenderer.js';
import { fetchCotizaciones, fetchEstadoBilletera, fetchHistorial, fetchVelas } from '../services/apiService.js';

document.addEventListener('DOMContentLoaded', () => {
    // Variables para mantener el estado actual del gráfico (qué ticker y qué temporalidad se está mostrando).
    let currentTicker = 'BTC';
    let currentInterval = '1d';
    // Bandera para evitar la carga concurrente del gráfico.
    let isChartLoading = false;

    /**
     * Actualiza la interfaz de usuario según el modo de trading (compra/venta).
     * @param {string} mode - El modo de operación ('comprar' o 'vender').
     */
    function setTradeMode(mode) {
        DOMElements.inputAccion.val(mode); 
        
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
        
        let tickerForBalance = '';
        if (UIState.esModoCompra()) {
            // Al comprar, el selector principal muestra todas las criptos disponibles (excepto USDT).
            const cryptosWithoutUSDT = window.allCryptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, cryptosWithoutUSDT, 'BTC');
            // El saldo a mostrar es el del token que se va a pagar.
            tickerForBalance = UIState.getTickerPago();
        } else {
            // Al vender, el selector principal muestra solo las criptos que el usuario posee.
            // Si no tiene ninguna, o si 'ownedCoins' aún no se ha cargado, manejamos el caso.
            if (!window.ownedCoins || window.ownedCoins.length === 0) {
                console.warn("WARN: window.ownedCoins no está disponible o está vacío al intentar configurar el modo de venta.");
                tickerForBalance = null; // No se puede mostrar un saldo si no hay monedas propias.
            } else {
                // Si hay monedas, usa la primera como predeterminada y la muestra.
                const defaultTicker = window.ownedCoins[0].ticker;
                tickerForBalance = FormLogic.popularSelector(DOMElements.selectorPrincipal, window.ownedCoins, defaultTicker);
            }
        }
        
        UIUpdater.mostrarSaldo(tickerForBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    /**
     * Función centralizada para obtener datos de velas y actualizar el gráfico.
     * @param {string} ticker El ticker de la criptomoneda (ej. 'BTC').
     * @param {string} interval La temporalidad del gráfico (ej. '1d', '15m').
     */
    async function actualizarGrafico(ticker, interval) {
        // Evita múltiples llamadas simultáneas si el usuario cambia rápido.
        if (isChartLoading) {
            console.log("Ignorando petición de gráfico, ya hay una en curso.");
            return;
        }
        isChartLoading = true;
        try {
            console.log(`📈 Pidiendo velas para ${ticker} en ${interval}...`);
            const nuevosDatosVelas = await fetchVelas(ticker, interval);
            updateChartData(nuevosDatosVelas); // Actualiza el gráfico con los nuevos datos.
        } catch (error) {
            console.error(`❌ Error al actualizar el gráfico para ${ticker}/${interval}:`, error);
            updateChartData([]); // Muestra el mensaje de error si falla la carga.
        } finally {
            isChartLoading = false; // Permite nuevas peticiones una vez completado.
        }
    }

    /**
     * Configura todos los event listeners para los elementos interactivos de la página.
     */
    function setupEventListeners() {
        // Listeners para cambiar el modo de trading (Comprar/Vender).
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        // Listener para cuando cambia la criptomoneda seleccionada.
        DOMElements.selectorPrincipal.on('change', () => {
            currentTicker = UIState.getTickerPrincipal(); // Actualiza el ticker global
            UIUpdater.actualizarLabelMonto(); // Actualiza la etiqueta del monto
            // Si estamos en modo de venta, muestra el saldo de la nueva criptomoneda.
            if (!UIState.esModoCompra()) {
                UIUpdater.mostrarSaldo(currentTicker);
            }
            // Pide y actualiza el gráfico con el nuevo ticker.
            actualizarGrafico(currentTicker, currentInterval);
        });

        // Listener para los botones de temporalidad (5m, 15m, 1h, etc.).
        $('#timeframe-selector').on('click', '.timeframe-btn', function() {
            const $btn = $(this);
            // Si el botón ya está activo, no hacer nada.
            if ($btn.hasClass('active')) return;

            // Actualiza el estilo visual para marcar el botón activo.
            $('#timeframe-selector .timeframe-btn').removeClass('active');
            $btn.addClass('active');

            // Actualiza el intervalo global y pide los nuevos datos para el gráfico.
            currentInterval = $btn.data('interval');
            actualizarGrafico(currentTicker, currentInterval);
        });

        // Listeners para los otros campos del formulario que afectan la UI pero no el gráfico.
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
     * Función principal de inicialización de la página de trading.
     * Carga todos los datos necesarios, inicializa componentes y configura listeners.
     */
    async function initialize() {
        try {
            // 1. Cargar todos los datos necesarios en paralelo.
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval) // Carga inicial para 'BTC' y temporalidad '1D'.
            ]);
            
            // 2. Poblar variables globales con los datos obtenidos.
            window.allCryptos = cotizaciones;
            window.ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.cantidad) > 0);
            
            // 3. Renderizar componentes que dependen de estos datos.
            UIUpdater.renderHistorial(historial);
            initializeChart(velas); // Inicializa el gráfico con los datos de velas.
            
            // 4. Inicializar componentes de terceros (Select2) para los selectores.
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({ 
                    width: '100%',
                    dropdownCssClass: 'text-dark', // Estilo para el dropdown
                    theme: "bootstrap-5"           // Usa el tema de Bootstrap 5 para coherencia
                });
            });

            // 5. Poblar los selectores con los datos cargados.
            FormLogic.popularSelector(DOMElements.selectorPagarCon, window.ownedCoins, 'USDT');
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.allCryptos, 'USDT');
            
            // 6. Configurar todos los event listeners.
            setupEventListeners();
            // Establecer el estado inicial de la interfaz (modo 'comprar').
            setTradeMode('comprar');
            // Asegurarse de que el botón '1D' de temporalidad esté activo visualmente al inicio.
            $('#timeframe-selector .timeframe-btn[data-interval="1d"]').addClass('active');

        } catch (error) {
            // Si algo falla en la carga inicial de datos, mostrar un mensaje de error global.
            console.error('Error fatal durante la inicialización:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales para la página de trading. Por favor, recarga la página.');
        }
    }

    // Iniciar el proceso de inicialización cuando el DOM esté listo.
    initialize();
});