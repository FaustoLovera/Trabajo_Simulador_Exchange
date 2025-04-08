function cargarTabla() {
    fetch("/datos_tabla")
      .then(res => res.json())
      .then(data => {
        const cuerpo = document.getElementById("tabla-datos");
        cuerpo.innerHTML = "";
  
        data.forEach(fila => {
          const tr = document.createElement("tr");
  
          fila.forEach(col => {
            const td = document.createElement("td");
            td.innerHTML = col;
            tr.appendChild(td);
          });
  
          cuerpo.appendChild(tr);
        });
      })
      .catch(error => {
        console.error("Error al cargar los datos:", error);
      });
  }
  
  document.addEventListener("DOMContentLoaded", cargarTabla);

  function actualizarDatosCada15Segundos() {
    setInterval(() => {
      fetch("/actualizar")
        .then(res => res.json())
        .then(data => {
          console.log("✅ Datos actualizados:", data);
          cargarTabla(); // vuelve a pedir y mostrar los datos actualizados
        });
    }, 15000); // 15 segundos
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    cargarTabla();
    actualizarDatosCada15Segundos();
  });