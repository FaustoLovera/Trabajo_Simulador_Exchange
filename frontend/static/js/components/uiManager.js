// frontend/static/js/components/uiManager.js

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { UIUpdater } from './uiUpdater.js';
import { FormLogic } from './formLogic.js';
import { AppState } from '../services/appState.js';
import { AppDataManager } from '../services/appDataManager.js';
import { updateChartData } from './chartRenderer.js';
import { fetchVelas } from '../services/apiService.js';
import { saveTradingState } from '../services/statePersistence.js';

export const UIManager = {
    currentTicker: 'BTC',
    currentInterval: '1d',
    isChartLoading: false,

    initialize(initialState) {
        this.currentTicker = initialState.ticker;
        this.currentInterval = initialState.interval;

        // Renderizar partes de la UI que no dependen del formulario
        UIUpdater.renderHistorial(initialState.historial);
        this.renderOrdenesAbiertas(initialState.ordenesAbiertas);
        
        // Preparar plugins y listeners de eventos
        this.setupSelect2();
        this.setupEventListeners(); // Mover aquí para que los listeners estén listos
        
        // --- SECUENCIA DE INICIALIZACIÓN CORREGIDA ---
        // 1. Establecer el modo por defecto ("comprar"). Esto muestra y oculta los campos correctos.
        this.setTradeMode('comprar'); 
        
        // 2. Ahora que los campos son visibles, poblamos y seleccionamos los valores.
        this.actualizarFormularioCompleto();
        
        // 3. Ajustamos el resto de los elementos.
        this.handleTipoOrdenChange();
        $('#timeframe-selector .timeframe-btn').removeClass('active').filter(`[data-interval="${this.currentInterval}"]`).addClass('active');
    },

    setupSelect2() {
        [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach((sel) => {
            sel.select2({ width: '100%', dropdownCssClass: 'text-dark', theme: 'bootstrap-5' });
        });
    },

    setupEventListeners() {
        DOMElements.botonComprar.on('click', () => this.handleTradeModeChange('comprar'));
        DOMElements.botonVender.on('click', () => this.handleTradeModeChange('vender'));
        DOMElements.selectorPrincipal.on('change', () => this.handleSelectorPrincipalChange());
        
        DOMElements.selectorPagarCon.on('change', () => this.updateDynamicLabels());
        DOMElements.selectorRecibirEn.on('change', () => this.updateDynamicLabels());
        
        $('#timeframe-selector').on('click', '.timeframe-btn', (e) => this.handleTimeframeChange(e));
        $('input[name="tipo-orden"]').on('change', () => this.handleTipoOrdenChange());
        DOMElements.radioModoIngreso.on('change', () => this.updateDynamicLabels());
        
        $('#precio_disparo, #precio_limite, #monto').on('input', (e) => this.validarInputNumerico(e));

        $('#tabla-ordenes-abiertas').on('click', '.btn-cancelar-orden', (e) => this.handleCancelClick(e));
    },

    /**
     * Función que se llama cuando el usuario hace clic en Comprar/Vender.
     * @param {string} mode - 'comprar' o 'vender'.
     */
    handleTradeModeChange(mode) {
        this.setTradeMode(mode);
        this.actualizarFormularioCompleto();
    },

    /**
     * Establece el estado visual básico del modo de trading (colores y visibilidad de campos).
     * Ya no llama a la actualización completa del formulario para evitar bucles.
     * @param {string} mode - 'comprar' o 'vender'.
     */
    setTradeMode(mode) {
        DOMElements.inputAccion.val(mode);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
    },

    /**
     * Rellena y actualiza todos los selectores y etiquetas del formulario.
     */
    actualizarFormularioCompleto() {
        const esCompra = UIState.esModoCompra();
        const ticker = this.currentTicker;
        
        if (esCompra) {
            FormLogic.popularSelector(DOMElements.selectorPrincipal, AppState.getAllCryptos().filter(c => c.ticker !== 'USDT'));
        } else {
            FormLogic.popularSelector(DOMElements.selectorPrincipal, AppState.getOwnedCoins().filter(c => c.ticker !== 'USDT'), 'No tienes monedas para vender');
        }
        DOMElements.selectorPrincipal.val(ticker).trigger('change.select2');
        
        FormLogic.actualizarOpcionesDeSelectores();
        this.updateDynamicLabels();
    },
    
    /**
     * Actualiza solo las etiquetas que cambian dinámicamente.
     */
    updateDynamicLabels() {
        const tickerParaBalance = UIState.esModoCompra() ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        UIUpdater.mostrarSaldo(tickerParaBalance);
        UIUpdater.actualizarLabelsModoIngreso();
        UIUpdater.actualizarLabelMonto();
    },

    handleSelectorPrincipalChange() {
        const nuevoTicker = UIState.getTickerPrincipal();
        if (!nuevoTicker || nuevoTicker === this.currentTicker) return;
        this.currentTicker = nuevoTicker;
        
        this.actualizarFormularioCompleto();
        this.actualizarGrafico();
        saveTradingState(this.currentTicker, this.currentInterval);
    },

    async actualizarGrafico() {
        if (!this.currentTicker || this.isChartLoading) return;
        this.isChartLoading = true;
        try {
            const nuevosDatosVelas = await fetchVelas(this.currentTicker, this.currentInterval);
            updateChartData(nuevosDatosVelas);
        } catch (error) {
            console.error(`Error al actualizar el gráfico para ${this.currentTicker}/${this.currentInterval}:`, error);
            updateChartData([]);
        } finally {
            this.isChartLoading = false;
        }
    },
    
    handleTimeframeChange(event) {
        this.currentInterval = $(event.currentTarget).data('interval');
        $(event.currentTarget).addClass('active').siblings().removeClass('active');
        this.actualizarGrafico();
        saveTradingState(this.currentTicker, this.currentInterval);
    },

    handleTipoOrdenChange() {
        const tipoOrden = $('input[name="tipo-orden"]:checked').val();
        const [campoStop, inputStop, labelStop] = [$('#campo-precio-disparo'), $('#precio_disparo'), $('#label-precio-disparo')];
        const [campoLimit, inputLimit] = [$('#campo-precio-limite'), $('#precio_limite')];

        [campoStop, campoLimit].forEach(f => f.hide());
        [inputStop, inputLimit].forEach(i => i.prop('required', false));
    
        if (tipoOrden === 'limit') {
            labelStop.text('Precio Límite');
            campoStop.show();
            inputStop.prop('required', true);
        } else if (tipoOrden === 'stop-limit') {
            labelStop.text('Precio Stop');
            campoStop.show();
            campoLimit.show();
            inputStop.prop('required', true);
            inputLimit.prop('required', true);
        }
        this.updateDynamicLabels();
    },

    renderOrdenesAbiertas(ordenes) {
        const tablaBody = $('#tabla-ordenes-abiertas tbody');
        if (!ordenes || ordenes.length === 0) {
            tablaBody.html('<tr><td colspan="7" class="text-center text-muted py-3">No hay órdenes abiertas.</td></tr>');
            return;
        } 
        
        const createOrdenAbiertaRowHTML = (orden) => {
            const fechaCreacion = new Date(orden.timestamp_creacion).toLocaleString('es-AR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
            const tipoOrdenClase = orden.accion === 'comprar' ? 'text-success' : 'text-danger';
            const cantidad = orden.cantidad_cripto_principal;
            const tickerCantidad = orden.accion === 'vender' ? orden.moneda_origen : orden.moneda_destino;
            const tipoOrdenFormatted = orden.tipo_orden.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            return `
                <tr>
                    <td class="text-start ps-3 small">${fechaCreacion}</td>
                    <td class="fw-bold">${orden.par}</td>
                    <td>${tipoOrdenFormatted}</td>
                    <td class="${tipoOrdenClase}">${orden.accion.charAt(0).toUpperCase() + orden.accion.slice(1)}</td>
                    <td>${orden.precio_disparo}</td>
                    <td>${cantidad} ${tickerCantidad}</td>
                    <td><button class="btn btn-sm btn-outline-danger btn-cancelar-orden" data-id-orden="${orden.id_orden}">Cancelar</button></td>
                </tr>`;
        };
        tablaBody.html(ordenes.map(createOrdenAbiertaRowHTML).join(''));
    },
    
    async handleCancelClick(event) {
        const orderId = $(event.currentTarget).data('id-orden');
        const result = await Swal.fire({
            title: '¿Estás seguro?', text: "No podrás revertir esta acción.",
            icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6', confirmButtonText: 'Sí, ¡cancelar orden!',
            cancelButtonText: 'No', background: '#212529', color: '#f8f9fa'
        });

        if (result.isConfirmed) {
            try {
                const respuesta = await AppDataManager.handleCancelOrder(orderId);
                Toast.fire({ icon: 'success', html: respuesta.mensaje });
                $(event.currentTarget).closest('tr').fadeOut(400, function() { $(this).remove(); });
                this.updateDynamicLabels();
            } catch (error) {
                Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo cancelar la orden.', background: '#212529', color: '#f8f9fa' });
            }
        }
    },

    validarInputNumerico(event, maxDecimales = 8) {
        const input = event.target;
        let value = input.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
        const parts = value.split('.');
        if (parts[1] && parts[1].length > maxDecimales) {
            value = parts[0] + '.' + parts[1].substring(0, maxDecimales);
        }
        input.value = value;
    }
};