// Centraliza todos los selectores del DOM en un único objeto para fácil acceso y mantenimiento.
export const DOMElements = {
    form: $('#formulario-trading'),
    selectorPrincipal: $('#cripto'),
    selectorPagarCon: $('#moneda-pago'),
    selectorRecibirEn: $('#moneda-recibir'),
    botonComprar: $('.boton-comprar'),
    botonVender: $('.boton-vender'),
    botonConfirmar: $('.boton-confirmar'),
    inputAccion: $('#accion'),
    campoPagarCon: $('#campo-pagar-con'),
    campoRecibirEn: $('#campo-recibir-en'),
    spanSaldoDisponible: $('#saldo-disponible'),
    radioModoIngreso: $('input[name="modo-ingreso"]'),
    labelMonto: $('label[for="monto"]'),
    inputMonto: $('#monto'),
    sliderMonto: $('#slider-monto'),
};