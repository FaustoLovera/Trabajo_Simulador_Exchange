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
    function obtenerPrecioDesdeAtributo(ticker) {
        let price = null;
        // Check origin select options first
        const origenOption = criptoOrigenSelect.querySelector(`option[value="${ticker}"]`);
        if (origenOption && origenOption.dataset.priceUsdt) {
            price = parseFloat(origenOption.dataset.priceUsdt);
        }
        // If not found in origin, check destination select options
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
            botonConfirmar.classList.remove('btn-danger'); // Ensure no lingering danger class
            botonConfirmar.classList.add('btn-success');
            botonConfirmar.textContent = 'CONFIRMAR COMPRA';
            sliderMonto.classList.remove('slider-venta');
            sliderMonto.classList.add('slider-compra');
            labelCriptoOrigen.textContent = 'Comprar con'; // Update label for origin crypto

            // Configure modo-ingreso options for 'compra'
            cantidadDestinoOption.classList.remove('d-none'); // Show "Cantidad de Cripto a Recibir"
            cantidadOrigenOption.classList.remove('d-none'); // Show "USDT a Gastar"
            valorUsdtOrigenOption.classList.add('d-none'); // Hide "Valor en USDT de Cripto a Vender"

            cantidadDestinoOption.textContent = 'Monto';
            cantidadOrigenOption.textContent = 'Total';
            
            // Set default modo-ingreso for buy
            modoIngresoUI.value = "cantidad_destino";
            
            // Ensure USDT is selected as origin for buying by default if available
            if (criptoOrigenSelect.querySelector('option[value="USDT"]')) {
                criptoOrigenSelect.value = 'USDT';
                // Trigger Select2 update if it's initialized on this element
                $('#cripto-origen').trigger('change.select2'); 
            }

        } else { // accion === 'venta'
            botonComprar.className = 'btn w-50 btn-outline-secondary boton-comprar';
            botonVender.className = 'btn w-50 btn-danger active boton-vender';
            botonConfirmar.classList.remove('btn-success'); // Ensure no lingering success class
            botonConfirmar.classList.add('btn-danger');
            botonConfirmar.textContent = 'CONFIRMAR VENTA';
            sliderMonto.classList.remove('slider-compra');
            sliderMonto.classList.add('slider-venta');
            labelCriptoOrigen.textContent = 'Vender'; // Update label for origin crypto

            // Configure modo-ingreso options for 'venta'
            cantidadDestinoOption.classList.add('d-none'); // Hide "Cantidad de Destino a Recibir" for sell
            cantidadOrigenOption.classList.remove('d-none'); // Show "Cantidad de Cripto a Vender"
            valorUsdtOrigenOption.classList.remove('d-none'); // Show "Valor en USDT de Cripto a Vender"

            cantidadOrigenOption.textContent = 'Monto';
            valorUsdtOrigenOption.textContent = 'Total';
            
            // Set default modo-ingreso for sell
            modoIngresoUI.value = "cantidad_origen"; 
            
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
                labelMonto.textContent = 'Monto';
            } else { // cantidad_origen
                montoInput.placeholder = 'Ej: 100 USDT';
                labelMonto.textContent = 'Total';
            }
        } else { // accion === 'venta'
            if (modoSeleccionado === 'cantidad_origen') {
                montoInput.placeholder = 'Ej: 0.1 ETH';
                labelMonto.textContent = 'Monto';
            } else { // valor_usdt_origen (only other option for selling)
                montoInput.placeholder = 'Ej: 200'; // Represents 200 USDT
                labelMonto.textContent = 'Total';
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
        const montoCalculado = (saldoValue * (porcentaje / 100)).toFixed(8);
        montoInput.value = parseFloat(montoCalculado); 
    });

    // Pre-submission logic: Handle 'valor_usdt_origen' conversion
    formularioTrading.addEventListener('submit', async function(event) {
        // Prevent default form submission
        event.preventDefault();

        const currentAccion = accionInput.value;
        const currentMonto = parseFloat(montoInput.value);
        const currentModoIngresoUI = modoIngresoUI.value;
        const currentOrigenTicker = criptoOrigenSelect.value;
        
        // If selling by USDT value of origin, convert monto to actual origin quantity
        if (currentAccion === 'venta' && currentModoIngresoUI === 'valor_usdt_origen') {
            const precioOrigenUsdt = obtenerPrecioDesdeAtributo(currentOrigenTicker); // Get price from data attributes
            
            if (precioOrigenUsdt === null || precioOrigenUsdt === 0 || isNaN(precioOrigenUsdt)) {
                alert(`Error: No se pudo obtener el precio de ${currentOrigenTicker} para calcular el valor en USDT.`);
                return; // Stop submission
            }
            const cantidadOrigenCalculada = (currentMonto / precioOrigenUsdt).toFixed(8); // Calculate actual crypto quantity
            montoInput.value = parseFloat(cantidadOrigenCalculada); // Update monto field
            modoIngresoBackend.value = "cantidad_origen"; // Change backend modo-ingreso to cantidad_origen
        } else {
            // For all other cases, the modo-ingreso is already set by the UI select (modoIngresoBackend.value)
            modoIngresoBackend.value = modoIngresoUI.value;
        }

        // Now, submit the form programmatically
        formularioTrading.submit();
    });

    // Initial setup on page load
    actualizarFormulario(); // Set up form based on default 'compra' mode
    actualizarSaldoDisponible(); // Display initial available balance
    actualizarTextoCampo(); // Apply initial label/placeholder for monto

});