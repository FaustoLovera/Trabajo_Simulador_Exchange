function cargarTabla() {
    fetch('/api/datos_tabla')
        .then((res) => res.text())
        .then((html) => {
            console.log("📥 HTML de la tabla de cotizaciones recibido.");
            const cuerpoTabla = document.getElementById('tabla-datos');
            if (cuerpoTabla) {
                cuerpoTabla.innerHTML = html;
            }
        })
        .catch((error) => {
            console.error('❌ Error al cargar los datos de la tabla:', error);
        });
}

function actualizarDatosCada15Segundos() {
    setInterval(() => {
        fetch('/api/actualizar')
            .then((res) => res.json())
            .then((data) => {
                console.log('✅ Datos de cotizaciones actualizados:', data);
                cargarTabla();
            })
            .catch((error) => {
                console.error('❌ Error al actualizar los datos:', error);
            });
    }, 15000); // Actualizar cada 15 segundos
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('tabla-datos')) {
        console.log("🚀 Inicializando carga de tabla de cotizaciones.");
        cargarTabla();
        actualizarDatosCada15Segundos();
    }
});