document.addEventListener('DOMContentLoaded', () => {

    // 1. SELECCIÓN DE ELEMENTOS
    const selectorPrincipal = $('#cripto'); // Usamos jQuery para consistencia
    const selectorPagarCon = $('#moneda-pago');
    const selectorRecibirEn = $('#moneda-recibir');

    const botonComprar = document.querySelector('.boton-comprar');
    const botonVender = document.querySelector('.boton-vender');
    const botonConfirmar = document.querySelector('.boton-confirmar');
    const campoPagarCon = document.getElementById('campo-pagar-con');
    const campoRecibirEn = document.getElementById('campo-recibir-en');
    const inputAccion = document.getElementById('accion');

    // 2. FUNCIÓN AUXILIAR PARA RELLENAR EL SELECTOR
    // Esta función funciona bien, la mantenemos.
    function actualizarSelector(selector, listaDeMonedas) {
        if (!selector.length) return; // Chequea si el elemento jQuery existe

        const valorSeleccionado = selector.val();
        selector.empty(); // Vacía opciones

        listaDeMonedas.forEach(moneda => {
            // Creamos una nueva opción de forma compatible
            const option = new Option(moneda.nombre, moneda.ticker, false, false);
            selector.append(option);
        });

        // Re-seleccionar el valor anterior si aún es válido
        if (listaDeMonedas.some(m => m.ticker === valorSeleccionado)) {
            selector.val(valorSeleccionado);
        }

        // Notificamos a Select2 de los cambios
        selector.trigger('change');
    }

    // 3. FUNCIONES PARA CAMBIAR DE MODO
    // (Con la corrección para el input 'accion' incluida)
    const activarModoCompra = () => {
        botonConfirmar.textContent = 'COMPRAR';
        botonComprar.className = 'btn w-50 btn-success active boton-comprar';
        botonVender.className = 'btn w-50 btn-outline-secondary boton-vender';
        botonConfirmar.className = 'btn w-100 btn-success boton-confirmar';

        if (inputAccion) inputAccion.value = 'comprar';

        // Rellenamos los selectores con los datos correctos
        actualizarSelector(selectorPrincipal, todasLasCriptos);
        actualizarSelector(selectorPagarCon, monedasPropias);

        if (campoPagarCon) campoPagarCon.style.display = 'block';
        if (campoRecibirEn) campoRecibirEn.style.display = 'none';
    };

    const activarModoVenta = () => {
        botonConfirmar.textContent = 'VENDER';
        botonComprar.className = 'btn w-50 btn-outline-secondary boton-comprar';
        botonVender.className = 'btn w-50 btn-danger active boton-vender';
        botonConfirmar.className = 'btn w-100 btn-danger boton-confirmar';
        
        if (inputAccion) inputAccion.value = 'vender';

        // Rellenamos los selectores con los datos correctos
        actualizarSelector(selectorPrincipal, monedasPropias);
        actualizarSelector(selectorRecibirEn, todasLasCriptos);

        if (campoPagarCon) campoPagarCon.style.display = 'none';
        if (campoRecibirEn) campoRecibirEn.style.display = 'block';
    };

    // ==========================================================
    // 4. INICIALIZACIÓN EN EL ORDEN CORRECTO (LA CLAVE)
    // ==========================================================

    // PASO A: Primero, establecemos el estado inicial del formulario.
    // Esto llama a activarModoCompra(), que rellena los selectores con sus opciones iniciales.
    activarModoCompra();

    // PASO B: AHORA que los <select> ya tienen <option>s dentro, los inicializamos con Select2.
    selectorPrincipal.select2({ width: '100%' });
    selectorPagarCon.select2({ width: '100%' });
    selectorRecibirEn.select2({ width: '100%' });

    // PASO C: Finalmente, asignamos los eventos para que los clicks funcionen.
    if (botonComprar && botonVender) {
        botonComprar.addEventListener('click', activarModoCompra);
        botonVender.addEventListener('click', activarModoVenta);
    }
});