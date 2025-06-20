// comportamientoFormulario.js (VERSIÓN FINAL Y ROBUSTA)

// Esperamos a que tanto el HTML como las variables globales (todasLasCriptos) estén listos.
document.addEventListener('DOMContentLoaded', () => {

    // 1. SELECCIÓN DE ELEMENTOS
    const selectorPrincipal = $('#cripto'); // Usamos jQuery para consistencia con Select2
    const selectorPagarCon = $('#moneda-pago');
    const selectorRecibirEn = $('#moneda-recibir');

    const botonComprar = document.querySelector('.boton-comprar');
    const botonVender = document.querySelector('.boton-vender');
    const botonConfirmar = document.querySelector('.boton-confirmar');
    const campoPagarCon = document.getElementById('campo-pagar-con');
    const campoRecibirEn = document.getElementById('campo-recibir-en');
    
    // Inicializamos todos los selectores con el plugin Select2 desde el principio
    selectorPrincipal.select2({ width: '100%' });
    selectorPagarCon.select2({ width: '100%' });
    selectorRecibirEn.select2({ width: '100%' });


    // 2. FUNCIÓN AUXILIAR PARA RELLENAR EL SELECTOR PRINCIPAL
    function actualizarSelectorPrincipal(listaDeMonedas) {
        if (!selectorPrincipal.length) return; // Chequea si el elemento existe

        const valorSeleccionado = selectorPrincipal.val();
        selectorPrincipal.empty(); // Vacía las opciones usando el método de jQuery

        listaDeMonedas.forEach(moneda => {
            const option = new Option(moneda.nombre, moneda.ticker, false, false);
            selectorPrincipal.append(option);
        });

        // Intentar re-seleccionar el valor si aún es válido
        if (listaDeMonedas.some(m => m.ticker === valorSeleccionado)) {
            selectorPrincipal.val(valorSeleccionado);
        }

        // Disparamos el evento 'change' de Select2 para notificar a todos los scripts
        selectorPrincipal.trigger('change');
    }

    // 3. FUNCIONES PARA CAMBIAR DE MODO
    const activarModoCompra = () => {
        // ... (código para cambiar estilos)
        botonConfirmar.textContent = 'COMPRAR';
        botonComprar.className = 'btn w-50 btn-success active boton-comprar';
        botonVender.className = 'btn w-50 btn-outline-secondary boton-vender';
        botonConfirmar.className = 'btn w-100 btn-success boton-confirmar';

        actualizarSelectorPrincipal(todasLasCriptos); // Rellena con la lista completa

        if (campoPagarCon) campoPagarCon.style.display = 'block';
        if (campoRecibirEn) campoRecibirEn.style.display = 'none';
    };

    const activarModoVenta = () => {
        // ... (código para cambiar estilos)
        botonConfirmar.textContent = 'VENDER';
        botonComprar.className = 'btn w-50 btn-outline-secondary boton-comprar';
        botonVender.className = 'btn w-50 btn-danger active boton-vender';
        botonConfirmar.className = 'btn w-100 btn-danger boton-confirmar';
        
        actualizarSelectorPrincipal(monedasPropias); // Rellena solo con las monedas del usuario

        if (campoPagarCon) campoPagarCon.style.display = 'none';
        if (campoRecibirEn) campoRecibirEn.style.display = 'block';
    };

    // 4. ASIGNACIÓN DE EVENTOS E INICIALIZACIÓN
    if (botonComprar && botonVender) {
        botonComprar.addEventListener('click', activarModoCompra);
        botonVender.addEventListener('click', activarModoVenta);
    }
    
    // Estado inicial: se activa el modo compra, que a su vez llama a actualizarSelectorPrincipal
    // y configura todo en el orden correcto.
    activarModoCompra();

    // La lógica para el label de Monto/Total no cambia y puede permanecer aquí si lo deseas.
});