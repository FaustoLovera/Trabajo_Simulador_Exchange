document.addEventListener('DOMContentLoaded', function() {
    const formularioTrading = document.getElementById('formulario-trading');
    const toggleTradeType = document.getElementById('toggle-trade-type');
    const accionInput = document.getElementById('accion'); // hidden input for 'compra'/'venta'
    const botonComprar = document.querySelector('.boton-comprar');
    const botonVender = document.querySelector('.boton-vender');
    const botonConfirmar = document.getElementById('boton-confirmar');
    const modoIngresoUI = document.getElementById('modo-ingreso-ui'); // The UI select for modo-ingreso
    const modoIngresoBackend = document.getElementById('modo-ingreso-backend'); // The hidden input for backend
    const criptoOrigenSelect = document.getElementById('cripto-origen');
    const criptoDestinoSelect = document.getElementById('cripto-destino');
    const labelCriptoOrigen = document.getElementById('label-cripto-origen');
    const montoInput = document.getElementById('monto');
    const sliderMonto = document.getElementById('slider-monto');
    const saldoDisponibleSpan = document.getElementById('saldo-disponible');
    const labelMonto = document.querySelector('label[for="monto"]'); // Agregamos esta línea para seleccionar el label del monto

    // Get all option elements for easier manipulation
    const cantidadDestinoOption = modoIngresoUI.querySelector('option[value="cantidad_destino"]');
    const cantidadOrigenOption = modoIngresoUI.querySelector('option[value="cantidad_origen"]');
    const valorUsdtOrigenOption = modoIngresoUI.querySelector('option[value="valor_usdt_origen"]');


    // --- Helper function to update available balance ---
    function actualizarSaldoDisponible() {
        const selectedOption = criptoOrigenSelect.options[criptoOrigenSelect.selectedIndex];
        const saldo = selectedOption && selectedOption.dataset.saldo ? selectedOption.dataset.saldo : '0.00000000';
        saldoDisponibleSpan.textContent = parseFloat(saldo).toFixed(8) + ' ' + criptoOrigenSelect.value;
        // Clear monto and reset slider when origin crypto changes or form updates
        montoInput.value = ''; 
        sliderMonto.value = 0; 
    }

    // --- Helper function to get current price from data attributes ---
    // Esta función ya no será necesaria en el frontend para el submit de valor_usdt_origen,
    // pero la mantenemos por si la usas para cálculos en tiempo real en la UI (que no es el caso actual).
    function obtenerPrecioDesdeAtributo(ticker) {
        let price = null;
        const origenOption = criptoOrigenSelect.querySelector(`option[value="${ticker}"]`);
        if (origenOption && origenOption.dataset.priceUsdt) {
            price = parseFloat(origenOption.dataset.priceUsdt);
        }
        if (price === null) {
            const destinoOption = criptoDestinoSelect.querySelector(`option[value="${ticker}"]`);
            if (destinoOption && destinoOption.dataset.priceUsdt) {
                price = parseFloat(destinoOption.dataset.priceUsdt);
            }
        }
        return price;
    }

    // --- Main function to update form based on 'Comprar'/'Vender' selection ---
    function actualizarFormulario() {
        const accion = accionInput.value; // 'compra' or 'venta'

        // Original logic for button styles and text
        if (accion === 'compra') {
            botonComprar.className = 'btn w-50 btn-success active boton-comprar';
            botonVender.className = 'btn w-50 btn-outline-secondary boton-vender';
            botonConfirmar.classList.remove('btn-danger'); 
            botonConfirmar.classList.add('btn-success');
            botonConfirmar.textContent = 'CONFIRMAR COMPRA';
            sliderMonto.classList.remove('slider-venta');
            sliderMonto.classList.add('slider-compra');
            labelCriptoOrigen.textContent = 'Comprar con';

            // Configure modo-ingreso options for 'compra'
            cantidadDestinoOption.classList.remove('d-none');
            cantidadOrigenOption.classList.remove('d-none');
            valorUsdtOrigenOption.classList.add('d-none');

            // Actualizar el texto de las opciones para Compra
            cantidadDestinoOption.textContent = 'Cantidad a Recibir';
            cantidadOrigenOption.textContent = 'USDT a Gastar';
            
            // Set default modo-ingreso for buy
            modoIngresoUI.value = "cantidad_destino";
            
            // Ensure USDT is selected as origin for buying by default if available
            if (criptoOrigenSelect.querySelector('option[value="USDT"]')) {
                criptoOrigenSelect.value = 'USDT';
                $('#cripto-origen').trigger('change.select2'); 
            }

        } else { // accion === 'venta'
            botonComprar.className = 'btn w-50 btn-outline-secondary boton-comprar';
            botonVender.className = 'btn w-50 btn-danger active boton-vender';
            botonConfirmar.classList.remove('btn-success'); 
            botonConfirmar.classList.add('btn-danger');
            botonConfirmar.textContent = 'CONFIRMAR VENTA';
            sliderMonto.classList.remove('slider-compra');
            sliderMonto.classList.add('slider-venta');
            labelCriptoOrigen.textContent = 'Vender';

            // Configure modo-ingreso options for 'venta'
            cantidadDestinoOption.classList.add('d-none'); // Ocultamos "Cantidad de USDT a Recibir"
            cantidadOrigenOption.classList.remove('d-none'); // Show "Cantidad de Cripto a Vender"
            valorUsdtOrigenOption.classList.remove('d-none'); // Show "Valor en USDT a Vender"

            // Actualizar el texto de las opciones para Venta
            cantidadOrigenOption.textContent = 'Cantidad de Cripto a Vender';
            valorUsdtOrigenOption.textContent = 'Valor en USDT a Vender';
            
            // Set default modo-ingreso for sell
            modoIngresoUI.value = "cantidad_origen"; // O podrías poner "valor_usdt_origen" si lo prefieres por defecto.
            
            // If USDT was selected as origin, try to switch to first non-USDT crypto available for selling
            const currentOrigin = criptoOrigenSelect.value;
            if (currentOrigin === 'USDT' && criptoOrigenSelect.options.length > 1) {
                const firstNonUsdtOption = Array.from(criptoOrigenSelect.options).find(opt => opt.value !== 'USDT');
                if (firstNonUsdtOption) {
                    criptoOrigenSelect.value = firstNonUsdtOption.value;
                    $('#cripto-origen').trigger('change.select2');
                }
            }
        }
        // Ensure the backend hidden input is set correctly after UI update
        // ESTA LÍNEA ES CRUCIAL y DEBE ESTAR AL FINAL DE actualizarFormulario
        modoIngresoBackend.value = modoIngresoUI.value; 
        actualizarSaldoDisponible(); // Update balance after changing origin crypto
        actualizarTextoCampo(); // Update label for monto field
    }

    // --- Original logic for dynamic label and placeholder based on modo-ingreso (adapted) ---
    const actualizarTextoCampo = () => {
        const modoSeleccionado = modoIngresoUI.value;
        const accion = accionInput.value; // 'compra' or 'venta'

        if (accion === 'compra') {
            if (modoSeleccionado === 'cantidad_destino') {
                montoInput.placeholder = 'Ej: 0.05 BTC';
                labelMonto.textContent = 'Cantidad a Recibir';
            } else { // cantidad_origen (USDT a Gastar)
                montoInput.placeholder = 'Ej: 100 USDT';
                labelMonto.textContent = 'Total a Gastar';
            }
        } else { // accion === 'venta'
            if (modoSeleccionado === 'cantidad_origen') { // Cantidad de Cripto a Vender
                montoInput.placeholder = 'Ej: 0.1 ETH';
                labelMonto.textContent = 'Cantidad a Vender';
            } else if (modoSeleccionado === 'valor_usdt_origen') { // Valor en USDT a Vender
                montoInput.placeholder = 'Ej: 200'; // Represents 200 USDT
                labelMonto.textContent = 'Valor en USDT a Vender';
            }
        }
    };


    // --- Event Listeners ---

    // Toggle between Comprar/Vender buttons
    toggleTradeType.addEventListener('click', function(event) {
        if (event.target.tagName === 'BUTTON') {
            accionInput.value = event.target.dataset.action; // Update hidden input
            actualizarFormulario();
        }
    });

    // Update balance when origin crypto changes
    criptoOrigenSelect.addEventListener('change', actualizarSaldoDisponible);

    // Update backend modo-ingreso and monto label when UI modo-ingreso changes
    modoIngresoUI.addEventListener('change', function() {
        modoIngresoBackend.value = modoIngresoUI.value;
        // Clear monto and reset slider when modo-ingreso changes
        montoInput.value = '';
        sliderMonto.value = 0;
        actualizarTextoCampo(); // Update label/placeholder immediately
    });

    // Handle slider input
    sliderMonto.addEventListener('input', function() {
        const saldoElement = saldoDisponibleSpan.textContent;
        const saldoValue = parseFloat(saldoElement.split(' ')[0]); // Get just the numeric part
        
        if (isNaN(saldoValue) || saldoValue <= 0) {
            montoInput.value = 0;
            return;
        }
        const porcentaje = parseFloat(sliderMonto.value);
        // NOTA: Para "Valor en USDT a Vender", el slider aplicaría un porcentaje del saldo en cripto,
        // no un porcentaje del valor en USDT. Esto podría ser confuso.
        // Si el modo es 'valor_usdt_origen', la lógica del slider debería ser diferente
        // para calcular un valor en USDT basado en un porcentaje del valor total del saldo.
        // Por ahora, lo dejamos así, pero es un punto a considerar para una mejora futura.

        const montoCalculado = (saldoValue * (porcentaje / 100)).toFixed(8);
        montoInput.value = parseFloat(montoCalculado); 
    });

    // Pre-submission logic: SIMPLIFICADA
    formularioTrading.addEventListener('submit', async function(event) {
        // Prevent default form submission
        event.preventDefault();

        // SIMPLEMENTE COPIAMOS EL VALOR DEL SELECT VISIBLE AL INPUT OCULTO
        // La conversión de 'valor_usdt_origen' a 'cantidad_origen' se hace en el backend (vender_cripto).
        modoIngresoBackend.value = modoIngresoUI.value; 

        // Ahora, submit the form programmatically
        formularioTrading.submit();
    });

    // Initial setup on page load
    actualizarFormulario();
    actualizarSaldoDisponible();
});