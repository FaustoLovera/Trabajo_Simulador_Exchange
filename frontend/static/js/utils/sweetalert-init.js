/**
 * @file Inicializador y configurador de SweetAlert2.
 * @module utils/sweetalert-init
 * @description Este archivo configura la librería `SweetAlert2` (que se asume disponible globalmente como `Swal`)
 * para crear un componente de notificación "Toast" personalizado y estandarizado. El `Toast` resultante
 * está diseñado para mostrar mensajes no intrusivos en la esquina superior derecha de la pantalla.
 */

/**
 * @global
 * @const {object}
 * @description Una instancia pre-configurada de `SweetAlert2` para mostrar notificaciones estilo "Toast".
 * Se define en el ámbito global para ser accesible desde cualquier parte de la aplicación, incluyendo
 * las plantillas renderizadas por el servidor (ej. para mostrar mensajes flash de Flask).
 *
 * @property {boolean} toast - `true` para el modo de notificación pequeña.
 * @property {string} position - `'top-end'` para ubicarla en la esquina superior derecha.
 * @property {boolean} showConfirmButton - `false` para no requerir interacción del usuario.
 * @property {number} timer - `8000` milisegundos para que desaparezca automáticamente.
 * @property {boolean} timerProgressBar - Muestra una barra de progreso para el temporizador.
 * @property {function} didOpen - Pausa el temporizador cuando el cursor está sobre la notificación.
 */
const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 8000,
    customClass: {
        popup: 'custom-toast-position'
    },
    timerProgressBar: true,
    showCloseButton: true,
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
    },
    background: '#343a40', // Fondo oscuro
    color: '#f8f9fa'       // Texto claro
});
