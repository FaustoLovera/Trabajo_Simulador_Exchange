document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formulario-trading');
    if (!form) return;

    // --- ELEMENTOS DEL DOM ---
    const selectorPrincipal = $('#cripto');
    const selectorPagarCon = $('#moneda-pago');
    const selectorRecibirEn = $('#moneda-recibir');
    const botonComprar = $('.boton-comprar');
    const botonVender = $('.boton-vender');
    const botonConfirmar = $('.boton-confirmar');
    const inputAccion = $('#accion');
    const campoPagarCon = $('#campo-pagar-con');
    const campoRecibirEn = $('#campo-recibir-en');
    const spanSaldoDisponible = $('#saldo-disponible');

    // --- INICIALIZACIÓN DE SELECT2 ---
    [selectorPrincipal, selectorPagarCon, selectorRecibirEn].forEach(sel => {
        sel.select2({ width: '100%', dropdownCssClass: 'text-dark' });
    });

    // --- FUNCIONES AUXILIARES ---

    function popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        lista.forEach(({ nombre, ticker }) => selector.append(new Option(nombre, ticker)));
        
        const valorFinal = (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) ? valorPorDefecto : (lista.length > 0 ? lista[0].ticker : null);

        if (valorFinal) {
            selector.val(valorFinal).trigger('change');
        } else {
            selector.trigger('change'); // Dispara el evento incluso si no hay valor
        }
        return valorFinal; // Devuelve el valor que se ha establecido
    }

    // Función para mostrar el saldo. Recibe el ticker explícitamente.
    function mostrarSaldo(ticker) {
        if (!ticker) {
            spanSaldoDisponible.text('--');
            return;
        }
        const saldo = billetera[ticker] || '0.00';
        const saldoFormateado = parseFloat(saldo).toFixed(8);
        spanSaldoDisponible.text(`${saldoFormateado} ${ticker}`);
    }


    // --- LÓGICA DE CONTROL DEL FORMULARIO ---

    function cambiarModo(modo) {
        const esCompra = modo === 'comprar';
        inputAccion.val(modo);
        
        // Actualizar la interfaz visual
        botonConfirmar.text(esCompra ? 'COMPRAR' : 'VENDER').toggleClass('btn-success', esCompra).toggleClass('btn-danger', !esCompra);
        botonComprar.toggleClass('active btn-success', esCompra).toggleClass('btn-outline-secondary', !esCompra);
        botonVender.toggleClass('active btn-danger', !esCompra).toggleClass('btn-outline-secondary', esCompra);
        
        campoPagarCon.toggle(esCompra);
        campoRecibirEn.toggle(!esCompra);

        // Habilitar/deshabilitar los selectores
        selectorPagarCon.prop('disabled', !esCompra);
        selectorRecibirEn.prop('disabled', esCompra);
        
        // Poblar el selector principal y obtener el ticker seleccionado
        let tickerParaSaldo = '';
        if (esCompra) {
            // Filtramos la lista para excluir 'USDT' antes de poblar el selector.
            const criptosSinUSDT = todasLasCriptos.filter(cripto => cripto.ticker !== 'USDT');
            popularSelector(selectorPrincipal, criptosSinUSDT, 'BTC');

            // En modo compra, el saldo que importa es el de la moneda de pago
            tickerParaSaldo = selectorPagarCon.val();
        } else {
            const tickerPorDefecto = monedasPropias.length > 0 ? monedasPropias[0].ticker : null;
            // En modo venta, el saldo que importa es el de la moneda principal (que acabamos de establecer)
            tickerParaSaldo = popularSelector(selectorPrincipal, monedasPropias, tickerPorDefecto);
        }

        // Llamamos a mostrarSaldo con el ticker que sabemos que es correcto AHORA MISMO.
        mostrarSaldo(tickerParaSaldo);
    }
    
    // --- EVENT LISTENERS ---

    botonComprar.on('click', () => cambiarModo('comprar'));
    botonVender.on('click', () => cambiarModo('vender'));

    // Los listeners ahora simplemente llaman a mostrarSaldo con el valor actual del selector.
    selectorPrincipal.on('change', () => {
        if (inputAccion.val() === 'vender') {
             mostrarSaldo(selectorPrincipal.val());
        }
    });

    selectorPagarCon.on('change', () => {
        if (inputAccion.val() === 'comprar') {
             mostrarSaldo(selectorPagarCon.val());
        }
    });

    // --- INICIALIZACIÓN ---
    // Poblar los selectores secundarios una sola vez al inicio
    popularSelector(selectorPagarCon, monedasPropias, 'USDT');
    popularSelector(selectorRecibirEn, todasLasCriptos, 'USDT');
    
    // Iniciar en modo compra
    cambiarModo('comprar');
});