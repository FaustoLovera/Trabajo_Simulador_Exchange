document.addEventListener("DOMContentLoaded", function () {
    // Billetera
    const tablaBilletera = document.getElementById("tabla-billetera");
    if (tablaBilletera) {
        fetch("/api/billetera")
            .then(response => response.json())
            .then(datos => {
                datos.forEach((cripto) => {
                    const decimalesCantidad = cripto.ticker === "USDT" ? 2 : 6;
                    const fila = document.createElement("tr");

                    fila.innerHTML = `
                        <td>${cripto.ticker}</td>
                        <td>${cripto.cantidad.toFixed(decimalesCantidad)}</td>
                        <td>$${cripto.precio_actual.toFixed(6)}</td>
                        <td>$${cripto.valor_usdt.toFixed(2)}</td>
                        <td style="color: ${cripto.ganancia_perdida >= 0 ? 'green' : 'red'};">
                            $${cripto.ganancia_perdida.toFixed(2)}
                        </td>
                        <td style="color: ${cripto.porcentaje_ganancia >= 0 ? 'green' : 'red'};">
                            ${cripto.porcentaje_ganancia.toFixed(2)}%
                        </td>
                        <td>${cripto.porcentaje.toFixed(2)}%</td>
                    `;

                    tablaBilletera.appendChild(fila);
                });
            })
            .catch(error => {
                console.error("Error al cargar los datos de la billetera:", error);
            });
    }

    // Historial
    const tablaHistorial = document.getElementById("tabla-historial");
    if (tablaHistorial) {
        fetch("/api/historial")
            .then(res => res.json())
            .then(historial => {
                historial.forEach(item => {
                    const fila = document.createElement("tr");
                    fila.innerHTML = `
                        <td style="color: ${item.tipo === 'compra' ? 'green' : 'red'}">${item.tipo}</td>
                        <td>${item.ticker}</td>
                        <td>${item.cantidad.toFixed(8)}</td>
                        <td>$${item.monto_usdt.toFixed(2)}</td>
                        <td>$${item.precio_unitario.toFixed(6)}</td>
                    `;
                    tablaHistorial.appendChild(fila);
                });
            })
            .catch(error => {
                console.error("Error al cargar el historial:", error);
            });
    }
});
