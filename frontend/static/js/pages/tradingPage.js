import { DOMElements } from '../components/domElements.js';
import { UIState } from '../components/uiState.js';
import { UIUpdater } from '../components/uiUpdater.js';
import { FormLogic } from '../components/formLogic.js';
import { initializeChart } from '../components/renderizarGraficoVelas.js';

// Este es el punto de entrada principal. Orquesta todos los módulos.
document.addEventListener('DOMContentLoaded', () => {

    async function fetchHistorial() {
        try {
            const response = await fetch('/api/historial');
            if (!response.ok) throw new Error('No se pudo cargar el historial');
            return await response.json();
        } catch (error) {
            console.error("Error al cargar historial:", error);
            return [];
        }
    }
    
    function cambiarModo(modo) {
        DOMElements.inputAccion.val(modo);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
        
        let tickerParaSaldo = '';
        if (UIState.esModoCompra()) {
            const criptosSinUSDT = window.todasLasCriptos.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, criptosSinUSDT, 'BTC');
            tickerParaSaldo = UIState.getTickerPago();
        } else {
            const tickerPorDefecto = window.monedasPropias.length > 0 ? window.monedasPropias[0].ticker : null;
            tickerParaSaldo = FormLogic.popularSelector(DOMElements.selectorPrincipal, window.monedasPropias, tickerPorDefecto);
        }
        
        UIUpdater.mostrarSaldo(tickerParaSaldo);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.resetSlider();
    }

    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => cambiarModo('comprar'));
        DOMElements.botonVender.on('click', () => cambiarModo('vender'));

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
            const valorCalculado = FormLogic.calcularMontoSlider();
            UIUpdater.setInputMonto(valorCalculado.toFixed(8));
        });
    }

    async function initialize() {
        // Inicializar Select2
        [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach(sel => {
            sel.select2({ width: '100%', dropdownCssClass: 'text-dark' });
        });
        
        // Poblar selectores
        FormLogic.popularSelector(DOMElements.selectorPagarCon, window.monedasPropias, 'USDT');
        FormLogic.popularSelector(DOMElements.selectorRecibirEn, window.todasLasCriptos, 'USDT');
        
        setupEventListeners();

        // Cargar y renderizar datos asíncronos
        const historial = await fetchHistorial();
        UIUpdater.renderHistorial(historial);
        
        initializeChart();
        
        cambiarModo('comprar');
    }

    initialize();
});