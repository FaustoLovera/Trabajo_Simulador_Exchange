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
import { 
    fetchCotizaciones, 
    fetchEstadoBilletera, 
    fetchHistorial, 
    fetchVelas, 
    fetchOrdenesAbiertas, 
    cancelarOrden 
} from '../services/apiService.js';
import { AppState } from '../services/appState.js';
import { saveTradingState, loadTradingState } from '../services/statePersistence.js';

function createOrdenAbiertaRowHTML(orden) {
    const fechaCreacion = new Date(orden.timestamp_creacion).toLocaleString('es-AR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    const tipoOrdenClase = orden.accion === 'comprar' ? 'text-success' : 'text-danger';
    const cantidad = orden.accion === 'comprar' ? orden.cantidad_destino : orden.cantidad_origen;
    const tickerCantidad = orden.par.split('/')[0];
    return `<tr><td class="text-start ps-3 small">${fechaCreacion}</td><td class="fw-bold">${orden.par}</td><td>${orden.tipo_orden.charAt(0).toUpperCase() + orden.tipo_orden.slice(1)}</td><td class="${tipoOrdenClase}">${orden.accion.charAt(0).toUpperCase() + orden.accion.slice(1)}</td><td>$${parseFloat(orden.precio_disparo).toFixed(4)}</td><td>${parseFloat(cantidad).toFixed(6)} ${tickerCantidad}</td><td><button class="btn btn-sm btn-outline-danger btn-cancelar-orden" data-id-orden="${orden.id_orden}">Cancelar</button></td></tr>`;
}

async function renderOrdenesAbiertas() {
    const tablaBody = $('#tabla-ordenes-abiertas');
    if (!tablaBody.length) return;
    try {
        const ordenes = await fetchOrdenesAbiertas();
        if (ordenes.length === 0) {
            tablaBody.html('<tr><td colspan="7" class="text-center text-muted py-3">No hay órdenes abiertas.</td></tr>');
        } else {
            tablaBody.html(ordenes.map(createOrdenAbiertaRowHTML).join(''));
        }
    } catch (error) {
        console.error("Error al renderizar órdenes abiertas:", error);
        tablaBody.html('<tr><td colspan="7" class="text-center text-danger py-3">Error al cargar órdenes.</td></tr>');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    let currentTicker;
    let currentInterval;
    let isChartLoading = false;

    function handleTipoOrdenChange() {
        const tipoOrden = $('input[name="tipo-orden"]:checked').val();
        const campoPrecioDisparo = $('#campo-precio-disparo');
        const inputPrecioDisparo = $('#precio_disparo');
        const labelPrecioDisparo = $('#label-precio-disparo');
        if (tipoOrden === 'market') {
            campoPrecioDisparo.hide();
            inputPrecioDisparo.prop('required', false);
            $('#modo-total').prop('disabled', false).parent().removeClass('disabled');
        } else {
            campoPrecioDisparo.show();
            inputPrecioDisparo.prop('required', true);
            labelPrecioDisparo.text(tipoOrden === 'limit' ? 'Precio Límite' : 'Precio Stop');
            $('#modo-monto').prop('checked', true).trigger('change');
            $('#modo-total').prop('disabled', true).parent().addClass('disabled');
        }
        UIUpdater.actualizarLabelMonto();
    }

    function actualizarFormularioUI() {
        const esCompra = UIState.esModoCompra();
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();
        if (esCompra) {
            const listaParaComprar = allCryptos.filter((c) => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, listaParaComprar, currentTicker);
        } else {
            const ownedCoinsToSell = ownedCoins.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, ownedCoinsToSell, currentTicker, 'No tienes monedas para vender');
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
        if (!ticker || isChartLoading) { return; }
        isChartLoading = true;
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
            actualizarFormularioUI();
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });
        DOMElements.selectorPagarCon.on('change', () => { UIUpdater.mostrarSaldo(UIState.getTickerPago()); UIUpdater.actualizarLabelMonto(); });
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
        $('input[name="tipo-orden"]').on('change', handleTipoOrdenChange);
        DOMElements.radioModoIngreso.on('change', UIUpdater.actualizarLabelMonto);
        DOMElements.sliderMonto.on('input', () => {
            const calculatedValue = FormLogic.calcularMontoSlider();
            UIUpdater.setInputMonto(calculatedValue.toFixed(8));
        });
        $('#tabla-ordenes-abiertas').on('click', '.btn-cancelar-orden', async function() {
            const $button = $(this);
            const orderId = $button.data('id-orden');
            $button.prop('disabled', true).text('...');
            try {
                const respuesta = await cancelarOrden(orderId);
                console.log(respuesta.mensaje);
                $button.closest('tr').fadeOut(400, function() { $(this).remove(); if ($('#tabla-ordenes-abiertas tr').length === 0) { renderOrdenesAbiertas(); } });
            } catch (error) {
                console.error(`Error al cancelar la orden ${orderId}:`, error);
                $button.prop('disabled', false).text('Cancelar');
                alert('Error al cancelar la orden. Por favor, refresca la página e intenta de nuevo.');
            }
        });
    }

    async function initialize() {
        console.log('Inicializando página de trading...');
        const urlParams = new URLSearchParams(window.location.search);
        const tickerDesdeUrl = urlParams.get('ticker');
        const savedState = loadTradingState();
        currentTicker = tickerDesdeUrl || savedState?.ticker || 'BTC';
        currentInterval = savedState?.interval || '1d';
        if (tickerDesdeUrl) saveTradingState(currentTicker, currentInterval);
        try {
            const [cotizaciones, estadoBilletera, historial, velas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchVelas(currentTicker, currentInterval),
            ]);

            AppState.setAllCryptos(cotizaciones);
            // CAMBIO CLAVE: Ahora el backend nos da los datos correctos para filtrar.
            const ownedCoins = estadoBilletera.filter((moneda) => parseFloat(moneda.cantidad) > 1e-8);
            AppState.setOwnedCoins(ownedCoins);

            renderOrdenesAbiertas();
            UIUpdater.renderHistorial(historial);
            initializeChart(velas);
            
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach((sel) => {
                sel.select2({ width: '100%', dropdownCssClass: 'text-dark', theme: 'bootstrap-5' });
            });

            setupEventListeners();
            setTradeMode('comprar');
            handleTipoOrdenChange();

            DOMElements.selectorPrincipal.val(currentTicker).trigger('change.select2');
            $('#timeframe-selector .timeframe-btn').removeClass('active').filter(`[data-interval="${currentInterval}"]`).addClass('active');

            console.log('Página de trading inicializada correctamente.');
        } catch (error) {
            console.error('Error fatal durante la inicialización de la página de trading:', error);
            UIUpdater.mostrarMensajeError('No se pudieron cargar los datos esenciales. Por favor, recarga la página.');
        }
    }

    initialize();
});