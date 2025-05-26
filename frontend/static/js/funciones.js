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
                cargarTabla(); // vuelve a pedir y mostrar los datos actualizados
            })
            .catch((error) => {
                console.error('❌ Error al actualizar datos:', error);
            });
    }, 15000); // 15 segundos
}

// Elementos del DOM, chequeo que existan
const criptoSelect = document.getElementById("cripto");
const parInput = document.getElementById("par");
const btnComprar = document.querySelector(".boton-comprar");
const btnVender = document.querySelector(".boton-vender");
const botonConfirmar = document.getElementById("boton-confirmar");

// Actualiza el campo oculto "par" con el valor seleccionado
function actualizarPar() {
    if (criptoSelect && parInput) {
        const cripto = criptoSelect.value;
        parInput.value = cripto + "USDT";
    }
}

// Inicialización
if (criptoSelect && parInput) {
    actualizarPar();
    criptoSelect.addEventListener("change", actualizarPar);
}

// Eventos para los botones comprar/vender, cambio de estilos y texto
if (btnComprar && btnVender && botonConfirmar) {
    btnComprar.addEventListener("click", () => {
        btnComprar.classList.add("btn-success", "active");
        btnComprar.classList.remove("btn-outline-secondary");

        btnVender.classList.remove("btn-danger", "active");
        btnVender.classList.add("btn-outline-secondary");

        botonConfirmar.classList.remove("btn-danger");
        botonConfirmar.classList.add("btn-success");
        botonConfirmar.textContent = "COMPRAR";
    });

    btnVender.addEventListener("click", () => {
        btnVender.classList.add("btn-danger", "active");
        btnVender.classList.remove("btn-outline-secondary");

        btnComprar.classList.remove("btn-success", "active");
        btnComprar.classList.add("btn-outline-secondary");

        botonConfirmar.classList.remove("btn-success");
        botonConfirmar.classList.add("btn-danger");
        botonConfirmar.textContent = "VENDER";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const botones = document.querySelectorAll("#toggle-trade-type button");
    const inputAccion = document.getElementById("accion");

    botones.forEach(boton => {
        boton.addEventListener("click", () => {
            // Quitar clases activas de todos
            botones.forEach(b => b.classList.remove("btn-success", "active"));
            botones.forEach(b => b.classList.add("btn-outline-secondary"));

            // Agregar clases activas al botón clickeado
            boton.classList.remove("btn-outline-secondary");
            boton.classList.add("btn-success", "active");

            // Cambiar valor oculto
            inputAccion.value = boton.getAttribute("data-action");
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    cargarTabla();
    actualizarDatosCada15Segundos();
});
