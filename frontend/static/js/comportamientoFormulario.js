document.addEventListener('DOMContentLoaded', () => {
    // Si no es la página de trading, no hacer nada.
    if (!document.getElementById('formulario-trading')) return;

    // 1. SELECCIÓN DE ELEMENTOS
    const selectorPrincipal = $('#cripto');
    const selectorPagarCon = $('#moneda-pago');
    const selectorRecibirEn = $('#moneda-recibir');

    const botonComprar = document.querySelector('.boton-comprar');
    const botonVender = document.querySelector('.boton-vender');
    const botonConfirmar = document.querySelector('.boton-confirmar');
    const inputAccion = document.getElementById('accion'); // El campo oculto
    
    const campoPagarCon = document.getElementById('campo-pagar-con');
    const campoRecibirEn = document.getElementById('campo-recibir-en');
    
    // Inicialización de Select2
    selectorPrincipal.select2({ theme: "bootstrap-5", width: '100%' });
    selectorPagarCon.select2({ theme: "bootstrap-5", width: '100%' });
    selectorRecibirEn.select2({ theme: "bootstrap-5", width: '100%' });

    // 2. FUNCIÓN PARA POBLAR SELECTORES
    function popularSelector(selector, lista, valorPorDefecto) {
        selector.empty();
        lista.forEach(moneda => {
            const option = new Option(moneda.nombre, moneda.ticker);
            selector.append(option);
        });
        if (valorPorDefecto && lista.some(m => m.ticker === valorPorDefecto)) {
            selector.val(valorPorDefecto).trigger('change');
        } else {
            selector.trigger('change');
        }
    }

    // 3. FUNCIONES PARA CAMBIAR DE MODO
    function activarModoCompra() {
        inputAccion.value = 'comprar'; // Asegura que el valor sea 'comprar'
        
        botonConfirmar.textContent = 'COMPRAR';
        botonComprar.classList.add('btn-success', 'active');
        botonComprar.classList.remove('btn-outline-secondary');
        botonVender.classList.remove('btn-danger', 'active');
        botonVender.classList.add('btn-outline-secondary');
        botonConfirmar.className = 'btn w-100 btn-success boton-confirmar';

        popularSelector(selectorPrincipal, todasLasCriptos, 'BTC');

        campoPagarCon.style.display = 'block';
        campoRecibirEn.style.display = 'none';
    }

    function activarModoVenta() {
        inputAccion.value = 'vender'; // Asegura que el valor sea 'vender'
        
        botonConfirmar.textContent = 'VENDER';
        botonVender.classList.add('btn-danger', 'active');
        botonVender.classList.remove('btn-outline-secondary');
        botonComprar.classList.remove('btn-success', 'active');
        botonComprar.classList.add('btn-outline-secondary');
        botonConfirmar.className = 'btn w-100 btn-danger boton-confirmar';
        
        popularSelector(selectorPrincipal, monedasPropias, monedasPropias.length > 0 ? monedasPropias[0].ticker : null);

        campoPagarCon.style.display = 'none';
        campoRecibirEn.style.display = 'block';
    }

    // 4. ASIGNACIÓN DE EVENTOS E INICIALIZACIÓN
    botonComprar.addEventListener('click', activarModoCompra);
    botonVender.addEventListener('click', activarModoVenta);
    
    activarModoCompra();
});