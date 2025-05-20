function cargarTabla() {
    fetch('/datos_tabla')
        .then((res) => res.text())
        .then((html) => {
            console.log("📥 HTML recibido:", html);
            const cuerpo = document.getElementById('tabla-datos');
            cuerpo.innerHTML = html;
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
                cargarTabla(); // vuelve a pedir y mostrar los datos actualizados
            });
    }, 15000); // 15 segundos
}

document.addEventListener('DOMContentLoaded', () => {
    cargarTabla();
    actualizarDatosCada15Segundos();
});

