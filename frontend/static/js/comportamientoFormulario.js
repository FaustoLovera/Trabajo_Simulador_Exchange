// CAMBIO DE MODO Y COLORES PARA BOTONES DE COMPRA Y VENTA
document.addEventListener('DOMContentLoaded', () => {
    const botonComprar = document.querySelector('.boton-comprar');
    const botonVender = document.querySelector('.boton-vender');
    const botonConfirmar = document.querySelector('.boton-confirmar');
    const slider = document.getElementById('slider-monto');

    const activarModoCompra = () => {
        botonComprar.className = 'btn w-50 btn-success active boton-comprar';
        botonVender.className = 'btn w-50 btn-outline-secondary boton-vender';
        botonConfirmar.className = 'btn w-100 btn-success boton-confirmar';
        botonConfirmar.textContent = 'COMPRAR';
        slider.classList.remove('slider-venta');
        slider.classList.add('slider-compra');
    };

    const activarModoVenta = () => {
        botonComprar.className = 'btn w-50 btn-outline-secondary boton-comprar';
        botonVender.className = 'btn w-50 btn-danger active boton-vender';
        botonConfirmar.className = 'btn w-100 btn-danger boton-confirmar';
        botonConfirmar.textContent = 'VENDER';
        slider.classList.remove('slider-compra');
        slider.classList.add('slider-venta');
    };

    botonComprar.addEventListener('click', activarModoCompra);
    botonVender.addEventListener('click', activarModoVenta);

    activarModoCompra();
});

// CAMBIO DINÁMICO DEL LABEL Y PLACEHOLDER SEGÚN MODO DE INGRESO
document.addEventListener('DOMContentLoaded', () => {
    const selectorModo = document.getElementById('modo-ingreso');
    const labelMonto = document.querySelector('label[for="monto"]');
    const inputMonto = document.getElementById('monto');

    const actualizarTextoCampo = () => {
        if (selectorModo.value === 'monto') {
            labelMonto.textContent = 'Monto (cantidad de cripto)';
            inputMonto.placeholder = 'Ej: 0.5 BTC';
        } else {
            labelMonto.textContent = 'Total (valor en USDT)';
            inputMonto.placeholder = 'Ej: 100 USDT';
        }
    };

    selectorModo.addEventListener('change', actualizarTextoCampo);
    actualizarTextoCampo(); // aplicar al cargar
});
