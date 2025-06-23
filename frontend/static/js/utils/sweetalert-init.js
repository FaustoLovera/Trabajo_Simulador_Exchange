/**
 * @file sweetalert-init.js
 * @description Inicializa y configura globalmente la librería SweetAlert2.
 * Define un objeto 'Toast' personalizado para notificaciones no intrusivas.
 */

// Se define 'Toast' en el ámbito global para que sea accesible
// desde otros scripts, como los flashes de Flask en el HTML.
const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3500,
    timerProgressBar: true,
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
    background: '#343a40', // Fondo oscuro
    color: '#f8f9fa'       // Texto claro
});
