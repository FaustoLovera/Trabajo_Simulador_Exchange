/**
 * @file Orquestador principal de la interfaz de usuario.
 * @module UIManager
 * @description Gestiona el estado de la UI, inicializa componentes, configura los listeners de eventos
 * y coordina las actualizaciones entre los diferentes módulos de la interfaz.
 * Actúa como el punto central de control para la interacción del usuario.
 */

import { DOMElements } from './domElements.js';
import { UIState } from './uiState.js';
import { UIUpdater } from './uiUpdater.js';
import { FormLogic } from './formLogic.js';
import { AppState } from '../services/appState.js';
import { AppDataManager } from '../services/appDataManager.js';
import { updateChartData } from './chartRenderer.js';
import { fetchVelas } from '../services/apiService.js';
import { saveTradingState } from '../services/statePersistence.js';

/**
 * @namespace UIManager
 * @description Objeto que encapsula toda la lógica de gestión de la interfaz de usuario.
 */
export const UIManager = {
    /** @type {string} El ticker de la criptomoneda actualmente seleccionada (ej. 'BTC'). */
    currentTicker: 'BTC',
    /** @type {string} El intervalo de tiempo actual para el gráfico (ej. '1d', '4h'). */
    currentInterval: '1d',
    /** @type {boolean} Flag para prevenir cargas múltiples y simultáneas del gráfico. */
    isChartLoading: false,

    /**
     * Inicializa la interfaz de usuario con el estado cargado.
     * Configura componentes, establece listeners y realiza el renderizado inicial.
     * La secuencia de inicialización es crítica para evitar condiciones de carrera en la UI.
     * @param {object} initialState - El estado inicial de la aplicación, que incluye ticker, intervalo, historial, etc.
     */
    initialize(initialState) {
        this.currentTicker = initialState.ticker;
        this.currentInterval = initialState.interval;

        UIUpdater.renderHistorial(initialState.historial);
        this.renderOrdenesAbiertas(initialState.ordenesAbiertas);
        
        this.setupSelect2();
        this.setupEventListeners();
        
        // Secuencia de inicialización del formulario:
        // 1. Establecer el modo (compra/venta) para asegurar la visibilidad correcta de los campos.
        this.setTradeMode('compra'); 
        // 2. Poblar los selectores y establecer valores ahora que los campos son visibles.
        this.actualizarFormularioCompleto();
        // 3. Ajustar campos dependientes del tipo de orden y el timeframe.
        this.handleTipoOrdenChange();
        $('#timeframe-selector .timeframe-btn').removeClass('active').filter(`[data-interval="${this.currentInterval}"]`).addClass('active');
    },

    /**
     * @private
     * Configura el plugin Select2 para los menús desplegables, mejorando su apariencia y funcionalidad.
     */
    setupSelect2() {
        [DOMElements.selectorPrincipal, DOMElements.selectorPagarCon, DOMElements.selectorRecibirEn].forEach((sel) => {
            sel.select2({ width: '100%', dropdownCssClass: 'text-dark', theme: 'bootstrap-5' });
        });
    },

    /**
     * @private
     * Centraliza la configuración de todos los listeners de eventos de la aplicación.
     */
    setupEventListeners() {
        DOMElements.form.on('submit', () => this.saveFormStateToStorage());
        DOMElements.botonComprar.on('click', () => this.handleTradeModeChange('compra'));
        DOMElements.botonVender.on('click', () => this.handleTradeModeChange('venta'));
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
     * @private
     * Maneja el cambio de modo de operación (compra/venta).
     * @param {('compra'|'venta')} mode - El modo de operación a activar.
     */
    handleTradeModeChange(mode) {
        this.setTradeMode(mode);
        this.actualizarFormularioCompleto();
    },

    /**
     * @private
     * Establece el estado visual del formulario para el modo de trading (colores, visibilidad de campos).
     * @param {('compra'|'venta')} mode - El modo de operación.
     */
    setTradeMode(mode) {
        DOMElements.inputAccion.val(mode);
        UIUpdater.actualizarBotones();
        UIUpdater.actualizarVisibilidadCampos();
    },

    /**
     * @private
     * Orquesta una actualización completa del formulario, repoblando selectores y actualizando etiquetas.
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
     * @private
     * Actualiza elementos de la UI que cambian frecuentemente, como saldos y etiquetas de campos.
     */
    updateDynamicLabels() {
        const tickerParaBalance = UIState.esModoCompra() ? UIState.getTickerPago() : UIState.getTickerPrincipal();
        UIUpdater.mostrarSaldo(tickerParaBalance);
        UIUpdater.actualizarLabelsModoIngreso();
        UIUpdater.actualizarLabelMonto();
    },

    /**
     * @private
     * Maneja el cambio en el selector principal de criptomonedas.
     */
    handleSelectorPrincipalChange() {
        const nuevoTicker = UIState.getTickerPrincipal();
        if (!nuevoTicker || nuevoTicker === this.currentTicker) return;
        this.currentTicker = nuevoTicker;
        
        this.actualizarFormularioCompleto();
        this.actualizarGrafico();
        saveTradingState(this.currentTicker, this.currentInterval);
    },

    /**
     * @private
     * Carga y actualiza los datos del gráfico de velas de forma asíncrona.
     */
    async actualizarGrafico() {
        if (!this.currentTicker || this.isChartLoading) return;
        this.isChartLoading = true;
        try {
            const nuevosDatosVelas = await fetchVelas(this.currentTicker, this.currentInterval);
            updateChartData(nuevosDatosVelas);
        } catch (error) {
            console.error(`Error al actualizar el gráfico para ${this.currentTicker}/${this.currentInterval}:`, error);
            updateChartData([]); // Limpia el gráfico en caso de error
        } finally {
            this.isChartLoading = false;
        }
    },
    
    /**
     * @private
     * Maneja el cambio de intervalo de tiempo para el gráfico.
     * @param {Event} event - El objeto de evento del clic.
     */
    handleTimeframeChange(event) {
        this.currentInterval = $(event.currentTarget).data('interval');
        $(event.currentTarget).addClass('active').siblings().removeClass('active');
        this.actualizarGrafico();
        saveTradingState(this.currentTicker, this.currentInterval);
    },

    /**
     * @private
     * Gestiona la visibilidad y obligatoriedad de los campos de precio según el tipo de orden.
     */
    handleTipoOrdenChange() {
        const tipoOrden = $('input[name="tipo-orden"]:checked').val();
        const campoStop = $('#campo-precio-disparo');
        const inputStop = $('#precio_disparo');
        const labelStop = $('#label-precio-disparo');
        const campoLimit = $('#campo-precio-limite');
        const inputLimit = $('#precio_limite');

        campoStop.hide();
        campoLimit.hide();
        inputStop.prop('required', false);
        inputLimit.prop('required', false);
    
        if (tipoOrden === 'limit') {
            labelStop.text('Precio Límite');
            campoStop.show();
            inputStop.prop('required', true);
        } else if (tipoOrden === 'stop-limit') {
            labelStop.text('Precio Stop');
            campoStop.show();
            inputStop.prop('required', true);
            
            campoLimit.show();
            inputLimit.prop('required', true);
        }
        this.updateDynamicLabels();
    },

    /**
     * Renderiza la tabla de órdenes abiertas con los datos proporcionados.
     * @param {Array<object>} ordenes - Un array de objetos, cada uno representando una orden abierta.
     */
    renderOrdenesAbiertas(ordenes) {
        const tablaBody = $('#tabla-ordenes-abiertas');
        if (!tablaBody.length) return;

        if (!ordenes || ordenes.length === 0) {
            tablaBody.html('<tr><td colspan="7" class="text-center py-3">No hay órdenes abiertas.</td></tr>');
            return;
        }
        
        const createOrdenAbiertaRowHTML = (orden) => {
            const fechaCreacion = new Date(orden.timestamp_creacion).toLocaleString('es-AR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
            const tipoOrdenClase = orden.accion === 'compra' ? 'text-success' : 'text-danger';
            const cantidad = orden.cantidad_cripto_principal;
            const tickerCantidad = orden.accion === 'venta' ? orden.moneda_origen : orden.moneda_destino;
            const tipoOrdenFormatted = orden.tipo_orden.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            return `
                <tr>
                    <td class="text-start ps-3 small">${fechaCreacion}</td>
                    <td class="fw-bold">${orden.par}</td>
                    <td>${tipoOrdenFormatted}</td>
                    <td class="${tipoOrdenClase}">${orden.accion.charAt(0).toUpperCase() + orden.accion.slice(1)}</td>
                    <td>${orden.precio_disparo}</td>
                    <td><button class="btn btn-sm btn-outline-danger btn-cancelar-orden" data-id-orden="${orden.id_orden}">Cancelar</button></td>
                </tr>`;
        };
        tablaBody.html(ordenes.map(createOrdenAbiertaRowHTML).join(''));
    },
    
    /**
     * @private
     * Maneja el clic en el botón 'Cancelar' de una orden abierta.
     * @param {Event} event - El objeto de evento del clic.
     */
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
                this.updateDynamicLabels(); // Actualizar saldo tras cancelación
            } catch (error) {
                Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo cancelar la orden.', background: '#212529', color: '#f8f9fa' });
            }
        }
    },

    /**
     * @private
     * Valida y sanea en tiempo real los campos de entrada numéricos.
     * @param {Event} event - El objeto de evento del input.
     * @param {number} [maxDecimales=8] - El número máximo de decimales permitidos.
     */
    validarInputNumerico(event, maxDecimales = 8) {
        const input = event.target;
        // Permite solo números y un punto decimal.
        let value = input.value.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
        const parts = value.split('.');
        if (parts[1] && parts[1].length > maxDecimales) {
            value = parts[0] + '.' + parts[1].substring(0, maxDecimales);
        }
        input.value = value;
    },
      /**
     * @private
     * Guarda el estado actual completo del formulario de trading en localStorage.
     * Se ejecuta justo antes de que el formulario se envíe.
     */
      saveFormStateToStorage() {
        const state = {
            accion: $('#accion').val(),
            ticker: $('#cripto').val(),
            monedaRecibir: $('#moneda-recibir').val(),
            monedaPagar: $('#moneda-pago').val(),
            tipoOrden: $('input[name="tipo-orden"]:checked').val(),
            precioDisparo: $('#precio_disparo').val(),
            precioLimite: $('#precio_limite').val(),
            modoIngreso: $('input[name="modo-ingreso"]:checked').val(),
            monto: $('#monto').val(),
        };
        // Convertimos el objeto a un string JSON y lo guardamos
        localStorage.setItem('tradingFormState', JSON.stringify(state));
        console.log("💾 Estado del formulario guardado en localStorage.", state);
    },

    /**
     * @private
     * Carga el estado del formulario desde localStorage y lo aplica a la UI.
     * Esto restaura las selecciones del usuario después de una recarga de página.
     */
    applyFormStateFromStorage() {
        const savedStateJSON = localStorage.getItem('tradingFormState');
        if (!savedStateJSON) return; // No hay estado guardado, no hacer nada

        console.log("🔄 Aplicando estado del formulario desde localStorage...");
        const state = JSON.parse(savedStateJSON);

        // Aplicar el estado a cada elemento del formulario
        this.setTradeMode(state.accion);
        $('#cripto').val(state.ticker).trigger('change.select2');
        $('#moneda-recibir').val(state.monedaRecibir);
        $('#moneda-pago').val(state.monedaPagar);
        
        // Seleccionar el radio button correcto
        $(`input[name="tipo-orden"][value="${state.tipoOrden}"]`).prop('checked', true).trigger('change');
        $(`input[name="modo-ingreso"][value="${state.modoIngreso}"]`).prop('checked', true);

        // Rellenar los campos de texto
        $('#precio_disparo').val(state.precioDisparo);
        $('#precio_limite').val(state.precioLimite);
        $('#monto').val(state.monto);

        // ¡MUY IMPORTANTE! Limpiar el estado para que no se aplique de nuevo en una recarga normal.
        localStorage.removeItem('tradingFormState');
        console.log("✅ Estado aplicado y localStorage limpiado.");
        
        // Forzar una actualización de todas las etiquetas y saldos después de restaurar
        this.actualizarFormularioCompleto();
    },
};