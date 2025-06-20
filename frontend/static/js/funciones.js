// Este archivo ahora solo contiene funciones globales usadas en otras partes del sitio.

function cargarTabla() {
    fetch('/datos_tabla')
        .then((res) => res.text())
        .then((html) => {
            console.log("📥 HTML recibido:", html);
            const cuerpo = document.getElementById('tabla-datos');
            if (cuerpo) {
                cuerpo.innerHTML = html;
            }
        })
        .catch((error) => {
            console.error('❌ Error al cargar los datos:', error);
        });
}

function actualizarDatosCada15Segundos() {
    setInterval(() => {
        fetch('/actualizar')
            .then((res) => res.json())
            .then((data) => {
                console.log('✅ Datos actualizados:', data);
                cargarTabla();
            })
            .catch((error) => {
                console.error('❌ Error al actualizar datos:', error);
            });
    }, 15000);
}

// La lógica del `parInput` también se queda si se usa en otra página.
function actualizarPar() {
    const criptoSelect = document.getElementById("cripto");
    const parInput = document.getElementById("par");
    if (criptoSelect && parInput) {
        parInput.value = criptoSelect.value + "USDT";
    }
}


// Inicialización para las páginas que usen estas funciones
document.addEventListener('DOMContentLoaded', () => {
    // Estas funciones solo se ejecutarán si la página actual
    // es la correcta (p.ej. la de Cotizaciones)
    if (document.getElementById('tabla-datos')) {
        cargarTabla();
        actualizarDatosCada15Segundos();
    }
    if (document.getElementById('par')) {
        const criptoSelect = document.getElementById("cripto");
        actualizarPar();
        criptoSelect.addEventListener("change", actualizarPar);
    }
});