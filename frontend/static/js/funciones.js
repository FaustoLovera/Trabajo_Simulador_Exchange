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
const criptoDestinoSelect = document.getElementById("cripto");
const parInput            = document.getElementById("par");
const btnComprar          = document.querySelector(".boton-comprar");
const btnVender           = document.querySelector(".boton-vender");
const botonConfirmar      = document.getElementById("boton-confirmar");

// ---------------------------
// NUEVO: Elementos para saldo
const criptoOrigenSelect = document.getElementById("cripto-origen");
const saldoDisponibleElem = document.getElementById("saldo-disponible");
// ---------------------------

// Actualiza el campo oculto "par" con el valor seleccionado de destino
function actualizarPar() {
    if (criptoDestinoSelect && parInput) {
        const cripto = criptoDestinoSelect.value;
        parInput.value = cripto + "USDT";
    }
}

// NUEVO: Actualiza el saldo disponible según la cripto origen
function actualizarSaldo() {
    if (!criptoOrigenSelect || !saldoDisponibleElem) return;

    const selectedOption = criptoOrigenSelect.options[criptoOrigenSelect.selectedIndex];
    const saldo = selectedOption.getAttribute("data-saldo");
    const ticker = selectedOption.value;

    if (saldo !== null) {
        saldoDisponibleElem.textContent = `${parseFloat(saldo).toFixed(8)} ${ticker}`;
    } else {
        saldoDisponibleElem.textContent = "--";
    }
}

// NUEVO: Pobla el select de cripto origen con el JSON recibido
function poblarCriptoOrigenDesdeObjeto() {
    fetch('/saldos') // Este endpoint debe devolver tu objeto JSON plano
        .then(res => res.json())
        .then(data => {
            if (!criptoOrigenSelect) return;

            criptoOrigenSelect.innerHTML = ""; // Limpia opciones previas

            for (const [ticker, saldo] of Object.entries(data)) {
                const option = document.createElement("option");
                option.value = ticker;
                option.textContent = ticker;
                option.setAttribute("data-saldo", saldo);
                criptoOrigenSelect.appendChild(option);
            }

            actualizarSaldo(); // Mostrar saldo de la primera opción
        })
        .catch((error) => {
            console.error("❌ Error al poblar criptos de origen:", error);
        });
}

// Inicialización para destino
if (criptoDestinoSelect && parInput) {
    actualizarPar();
    criptoDestinoSelect.addEventListener("change", actualizarPar);
}

// Inicialización para origen (saldo)
if (criptoOrigenSelect && saldoDisponibleElem) {
    criptoOrigenSelect.addEventListener("change", actualizarSaldo);
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

    // Iniciar carga de tabla y actualización periódica
    cargarTabla();
    actualizarDatosCada15Segundos();

    // NUEVO: cargar cripto origen desde el JSON
    poblarCriptoOrigenDesdeObjeto();
});