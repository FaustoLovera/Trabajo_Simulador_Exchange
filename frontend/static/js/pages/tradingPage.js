// frontend/static/js/pages/tradingPage.js

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
    const cantidad = orden.cantidad_cripto_principal; 
    const tickerCantidad = orden.accion === 'vender' ? orden.moneda_origen : orden.moneda_destino;
    return `<tr><td class="text-start ps-3 small">${fechaCreacion}</td><td class="fw-bold">${orden.par}</td><td>${orden.tipo_orden.charAt(0).toUpperCase() + orden.tipo_orden.slice(1)}</td><td class="${tipoOrdenClase}">${orden.accion.charAt(0).toUpperCase() + orden.accion.slice(1)}</td><td>$${parseFloat(orden.precio_disparo).toFixed(4)}</td><td>${parseFloat(cantidad).toFixed(6)} ${tickerCantidad}</td><td><button class="btn btn-sm btn-outline-danger btn-cancelar-orden" data-id-orden="${orden.id_orden}">Cancelar</button></td></tr>`;
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
    

        const campoPrecioLimite = $('#campo-precio-limite');
        const inputPrecioLimite = $('#precio_limite');
    

        campoPrecioDisparo.hide();
        campoPrecioLimite.hide();
        inputPrecioDisparo.prop('required', false);
        inputPrecioLimite.prop('required', false);
    
        if (tipoOrden === 'limit') {
            labelPrecioDisparo.text('Precio Límite'); // Lo llamamos "Precio Límite"
            campoPrecioDisparo.show();
            inputPrecioDisparo.prop('required', true);
    
        } else if (tipoOrden === 'stop-limit') { // Cambiado de 'stop-loss'
            labelPrecioDisparo.text('Precio Stop'); // Ahora este es el "Precio Stop"
            campoPrecioDisparo.show();
            campoPrecioLimite.show(); // Mostramos el segundo campo
            inputPrecioDisparo.prop('required', true);
            inputPrecioLimite.prop('required', true); // Ambos son requeridos
        }
        
        // Para 'market', no se hace nada, ambos campos permanecen ocultos.
        UIUpdater.actualizarLabelMonto();
    }

    // El resto del archivo no necesita cambios significativos
    function actualizarFormularioUI() {
        const esCompra = UIState.esModoCompra();
        const allCryptos = AppState.getAllCryptos();
        const ownedCoins = AppState.getOwnedCoins();
        DOMElements.selectorPrincipal.off('change');
        if (esCompra) {
            const listaParaComprar = allCryptos.filter((c) => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, listaParaComprar);
        } else {
            const ownedCoinsToSell = ownedCoins.filter(c => c.ticker !== 'USDT');
            FormLogic.popularSelector(DOMElements.selectorPrincipal, ownedCoinsToSell, 'No tienes monedas para vender');
        }
        DOMElements.selectorPrincipal.val(currentTicker);
        DOMElements.selectorPrincipal.on('change', handleSelectorPrincipalChange);
        FormLogic.actualizarOpcionesDeSelectores();
        const tickerParaBalance = esCompra ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        UIUpdater.mostrarSaldo(tickerParaBalance);
        UIUpdater.actualizarLabelMonto();
        UIUpdater.actualizarLabelsModoIngreso();
    }

    function handleSelectorPrincipalChange() {
        const nuevoTicker = UIState.getTickerPrincipal();
        if (!nuevoTicker || nuevoTicker === currentTicker) return;
        currentTicker = nuevoTicker;
        actualizarFormularioUI();
        actualizarGrafico(currentTicker, currentInterval);
        saveTradingState(currentTicker, currentInterval);
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
    
    function validarInputNumerico(event, maxDecimales = 8) {
        const input = event.target;
        let value = input.value;
        value = value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
        const parts = value.split('.');
        if (parts[1] && parts[1].length > maxDecimales) {
            value = parts[0] + '.' + parts[1].substring(0, maxDecimales);
        }
        if (input.value !== value) {
            input.value = value;
        }
    }
    
    function setupEventListeners() {
        DOMElements.botonComprar.on('click', () => setTradeMode('comprar'));
        DOMElements.botonVender.on('click', () => setTradeMode('vender'));
        DOMElements.selectorPrincipal.on('change', handleSelectorPrincipalChange);
        
        DOMElements.selectorPagarCon.on('change', () => {
            UIUpdater.mostrarSaldo(UIState.getTickerPago());
            UIUpdater.actualizarLabelMonto();
            UIUpdater.actualizarLabelsModoIngreso();
        });
        
        DOMElements.selectorRecibirEn.on('change', () => {
            UIUpdater.actualizarLabelMonto();
            UIUpdater.actualizarLabelsModoIngreso();
        });
        
        $('#timeframe-selector').on('click', '.timeframe-btn', function () {
            currentInterval = $(this).data('interval');
            $(this).addClass('active').siblings().removeClass('active');
            actualizarGrafico(currentTicker, currentInterval);
            saveTradingState(currentTicker, currentInterval);
        });

        $('input[name="tipo-orden"]').on('change', handleTipoOrdenChange);
        DOMElements.radioModoIngreso.on('change', UIUpdater.actualizarLabelMonto);
        
        DOMElements.inputMonto.on('input', (e) => validarInputNumerico(e, 8));
        $('#precio_disparo').on('input', (e) => validarInputNumerico(e, 8));

        $('#tabla-ordenes-abiertas').on('click', '.btn-cancelar-orden', function() {
            const orderId = $(this).data('id-orden');
            Swal.fire({
                title: '¿Estás seguro?', text: "No podrás revertir esta acción.",
                icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6', confirmButtonText: 'Sí, ¡cancelar orden!',
                cancelButtonText: 'No', background: '#212529', color: '#f8f9fa'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const respuesta = await cancelarOrden(orderId);
                        Toast.fire({ icon: 'success', html: respuesta.mensaje });
                        $(this).closest('tr').fadeOut(400, function() { $(this).remove(); if ($('#tabla-ordenes-abiertas tr').length === 0) {
                            const tablaBody = $('#tabla-ordenes-abiertas');
                            tablaBody.html('<tr><td colspan="7" class="text-center text-muted py-3">No hay órdenes abiertas.</td></tr>');
                        }});
                    } catch (error) {
                        Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo cancelar la orden.', background: '#212529', color: '#f8f9fa' });
                    }
                }
            });
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
            const [cotizaciones, estadoBilletera, historial, ordenesAbiertas] = await Promise.all([
                fetchCotizaciones(), fetchEstadoBilletera(), fetchHistorial(), fetchOrdenesAbiertas()
            ]);

            AppState.setAllCryptos(cotizaciones);
            AppState.setOwnedCoins(estadoBilletera);

            UIUpdater.renderHistorial(historial);
            const tablaOrdenesBody = $('#tabla-ordenes-abiertas');
            if (ordenesAbiertas.length === 0) {
                tablaOrdenesBody.html('<tr><td colspan="7" class="text-center text-muted py-3">No hay órdenes abiertas.</td></tr>');
            } else {
                tablaOrdenesBody.html(ordenesAbiertas.map(createOrdenAbiertaRowHTML).join(''));
            }

            const datosVelas = await fetchVelas(currentTicker, currentInterval);
            initializeChart(datosVelas);
            
            [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach((sel) => {
                sel.select2({ width: '100%', dropdownCssClass: 'text-dark', theme: 'bootstrap-5' });
            });

            setupEventListeners();
            setTradeMode('comprar');
            handleTipoOrdenChange();

            $('#timeframe-selector .timeframe-btn').removeClass('active').filter(`[data-interval="${currentInterval}"]`).addClass('active');

            console.log('Página de trading inicializada correctamente.');
        } catch (error) {
            console.error('Error fatal durante la inicialización:', error);
            Swal.fire({
                icon: 'error', title: 'Error de Conexión',
                text: 'No se pudieron cargar los datos esenciales. Por favor, recarga la página.',
                background: '#212529', color: '#f8f9fa'
            });
        }
    }

    initialize();
});