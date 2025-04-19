document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/billetera");
        const datos = await res.json();

        const tbody = document.getElementById("tabla-billetera");
        const saldoElement = document.getElementById("saldo-usd");

        let totalUSD = 0;

        // Calcular total para porcentaje
        for (let cripto of datos) {
            const valorUSD = cripto.cantidad * cripto.precio_usd;
            if (valorUSD > 0.00001) {
                totalUSD += valorUSD;
            }
        }

        // Mostrar en la tabla
        for (let cripto of datos) {
            const valorUSD = cripto.cantidad * cripto.precio_usd;

            // Ignorar las que tienen 0
            if (valorUSD < 0.00001) continue;

            const porcentaje = ((valorUSD / totalUSD) * 100).toFixed(2);

            const fila = `
                <tr>
                    <td>${cripto.ticker}</td>             <!-- Criptomoneda -->
                    <td>${cripto.cantidad.toFixed(8)}</td> <!-- Cantidad -->
                    <td>${valorUSD.toFixed(2)} USDT</td>  <!-- Valor en USDT -->
                    <td>${porcentaje}%</td>              <!-- % del total -->
                </tr>
            `;
            tbody.innerHTML += fila;
        }

        saldoElement.textContent = `${totalUSD.toFixed(2)} USDT`;
    } catch (error) {
        console.error("Error al cargar la billetera:", error);
    }
});
