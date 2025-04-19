fetch("/api/billetera")
  .then((response) => response.json())
  .then((data) => {
    const tabla = document.getElementById("tabla-billetera");

    let saldoUSD = 0;

    for (let moneda in data) {
      const cantidad = data[moneda].cantidad;
      const porcentaje = data[moneda].porcentaje;

      if (moneda === "USDT") {
        saldoUSD = cantidad;
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${moneda}</td>
        <td>${cantidad.toFixed(8)}</td>
        <td>${porcentaje.toFixed(4)}%</td>
        <td>--</td>
      `;
      tabla.appendChild(tr);
    }

    document.getElementById("saldo-usd").innerText = saldoUSD.toFixed(2);
  })
  .catch((error) => console.log("Error al cargar los datos:", error));
