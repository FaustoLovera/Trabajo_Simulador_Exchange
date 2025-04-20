document.addEventListener("DOMContentLoaded", async function () {
    const tabla = document.getElementById("tabla-billetera");

    try {
        const response = await fetch("/api/billetera");
        const datos = await response.json();

        datos.forEach((cripto) => {
            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${cripto.ticker}</td>
                <td>${cripto.cantidad.toFixed(6)}</td>
                <td>$${cripto.precio_actual.toFixed(2)}</td>
                <td>$${cripto.valor_usdt.toFixed(2)}</td>
                <td style="color: ${cripto.ganancia_perdida >= 0 ? 'green' : 'red'};">
                    $${cripto.ganancia_perdida.toFixed(2)}
                </td>
                <td style="color: ${cripto.porcentaje_ganancia >= 0 ? 'green' : 'red'};">
                    ${cripto.porcentaje_ganancia.toFixed(2)}%
                </td>
                <td>${cripto.porcentaje.toFixed(2)}%</td>
            `;

            tabla.appendChild(fila);
        });
    } catch (error) {
        console.error("Error al cargar los datos de la billetera:", error);
    }
});


