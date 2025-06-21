// Orquesta la inicialización y la lógica principal de la página de trading.
// Orquesta la inicialización y la lógica principal de la página de trading.
import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart } from '../components/chartRenderer.js';
import { fetchCotizaciones, fetchEstadoBilletera, fetchHistorial, fetchVelas } from '../services/apiService.js';

document.addEventListener('DOMContentLoaded', () => {
    // Variables globales para almacenar datos
    window.allCryptos = [];
    window.ownedCoins = [];

    function setTradeMode(mode) {
        DOMElements.inputAccion.val(modo);
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

    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        DOMElements.selectorPrincipal.on('change', () => {
            UIUpdater.actualizarLabelMonto();
            if (!UIState.esModoCompra()) UIUpdater.mostrarSaldo(UIState.getTickerPrincipal());
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

    // Función principal de inicialización
    async function initialize() {
        try {
            // 1. Cargar todos los datos necesarios en paralelo desde el servicio de API
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas()
            ]);
            
            // 2. Actualizar variables globales
            window.allCryptos = cotizaciones;
            window.ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.saldo) > 0);
            
            // 3. Renderizar componentes que dependen de los datos
            UIUpdater.renderHistorial(historial);
            initializeChart(velas);
            
            // 4. Inicializar componentes de UI (Select2, etc.)
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({ width: '100%', dropdownCssClass: 'text-dark' });
            });

            // 5. Poblar los selectores con los datos ya cargados
            FormLogic.popularSelector(DOMElements.selectorPagarCon, window.ownedCoins, 'USDT');
            FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.allCryptos, 'USDT');
            
            // 6. Configurar listeners y estado inicial
            setupEventListeners();
            setTradeMode('comprar');

        } catch (error) {
            console.error('Error fatal durante la inicialización:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales para la página de trading. Por favor, recarga la página.');
        }
    }

    // Iniciar la aplicación
    initialize();
});