// Orquesta la inicialización y la lógica principal de la página de trading.
import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart } from '../components/chartRenderer.js';
import { fetchCotizaciones, fetchEstadoBilletera, fetchHistorial, fetchVelas } from '../services/apiService.js';

console.log("1. tradingPage.js - Script cargado e importaciones OK");

document.addEventListener('DOMContentLoaded', () => {
    console.log("2. tradingPage.js - DOMContentLoaded se disparó");

    // Variables globales para almacenar datos
    window.allCryptos = [];
    // Declaración explícita de window.ownedCoins
    window.ownedCoins = []; 

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
            const cryptosWithoutUSDT = window.allCryptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, cryptosWithoutUSDT, 'BTC');
            tickerForBalance = UIState.getTickerPago();
        } else {
            // Usamos window.ownedCoins aquí.
            // Si window.ownedCoins es null o undefined o vacío, puede causar problemas.
            // Añadimos una comprobación defensiva aquí.
            if (!window.ownedCoins || window.ownedCoins.length === 0) {
                console.warn("WARN: window.ownedCoins no está disponible o está vacío al intentar configurar el modo de venta.");
                // Podríamos intentar poblar con algo genérico o simplemente no hacer nada.
                // Por ahora, si no hay ownedCoins, no poblamos el selector principal.
                tickerForBalance = null; // O manejarlo de otra forma
            } else {
                const defaultTicker = window.ownedCoins[0].ticker; // Accede al primer elemento si existe
                tickerForBalance = FormLogic.popularSelector(DOMElements.selectorPrincipal, window.ownedCoins, defaultTicker);
            }
        }
        
        UIUpdater.mostrarSaldo(tickerForBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    /**
     * Configura todos los event listeners para los elementos interactivos del formulario y el gráfico.
     */
    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));

        DOMElements.selectorPrincipal.on('change', () => {
            UIUpdater.actualizarLabelMonto();
            if (!UIState.esModoCompra()) {
                // Aquí también puede ser que window.ownedCoins no esté listo si el usuario cambia a venta muy rápido.
                // Pero la protección en setTradeMode debería mitigar esto.
                UIUpdater.mostrarSaldo(UIState.getTickerPrincipal());
            }
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
        console.log("3. tradingPage.js - Entrando en initialize()");
        try {
            console.log("4. tradingPage.js - A punto de llamar a Promise.all");
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas()
            ]);
            console.log("5. tradingPage.js - Promise.all completado con ÉXITO");
            
            window.allCryptos = cotizaciones;
            // CORRECCIÓN: Asegurarse de usar 'ownedCoins' y filtrar correctamente
            window.ownedCoins = estadoBilletera.filter(moneda => parseFloat(moneda.cantidad) > 0);
            console.log(`6. tradingPage.js - Variables globales pobladas: allCryptos=${window.allCryptos.length}, ownedCoins=${window.ownedCoins.length}`);

            UIUpdater.renderHistorial(historial);
            initializeChart(velas);
            console.log("7. tradingPage.js - Historial y gráfico renderizados");

            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
                sel.select2({ 
                    width: '100%', 
                    dropdownCssClass: 'text-dark', 
                    theme: 'bootstrap-5' 
                });
            });
            console.log("8. tradingPage.js - Select2 inicializado");

            // 5. Poblar los selectores con los datos ya cargados
            // Asegurarse de que window.ownedCoins está disponible ANTES de poblar el selector
            if (window.ownedCoins) {
                FormLogic.popularSelector(DOMElements.selectorPagarCon, window.ownedCoins, 'USDT');
            } else {
                console.warn("WARN: window.ownedCoins no está disponible al poblar selectorPagarCon.");
                // Poblar con un valor por defecto si ownedCoins no existe
                FormLogic.popularSelector(DOMElements.selectorPagarCon, [{ticker: 'USDT', nombre: 'USDT'}], 'USDT');
            }
            // Siempre poblar el selector Recibir en con allCryptos
            if (window.allCryptos) {
                FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.allCryptos, 'USDT');
            } else {
                console.warn("WARN: window.allCryptos no está disponible al poblar selectorRecibirEn.");
            }
            console.log("9. tradingPage.js - Selectores poblados");
            
            setupEventListeners();
            setTradeMode('comprar'); // Iniciar en modo compra por defecto
            console.log("10. tradingPage.js - Listeners y modo de trading configurados. ¡Inicialización COMPLETA!");

        } catch (error) {
            console.error('--- ERROR FATAL CAPTURADO EN INITIALIZE ---', error); 
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales para la página de trading. Por favor, recarga la página.');
        }
    }

    initialize();
});