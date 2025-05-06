document.addEventListener("DOMContentLoaded", function () {
    // Billetera
    const tablaBilletera = document.getElementById("tabla-billetera");
    if (tablaBilletera) {
        fetch("/api/billetera")
            .then(res => res.text())
            .then(html => {
                tablaBilletera.innerHTML = html;
            })
            .catch(error => {
                console.error("Error al cargar los datos de la billetera:", error);
            });
    }

    // Historial
    const tablaHistorial = document.getElementById("tabla-historial");
    if (tablaHistorial) {
        fetch("/api/historial")
            .then(res => res.text())
            .then(html => {
                tablaHistorial.innerHTML = html;
            })
            .catch(error => {
                console.error("Error al cargar el historial:", error);
            });
    }
});
