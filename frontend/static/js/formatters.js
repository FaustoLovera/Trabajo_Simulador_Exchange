// Este módulo replica los filtros de formato de Jinja en JavaScript.

/**
 * Formatea un número como un valor monetario.
 * @param {string|number} valor El número a formatear.
 * @param {number} decimales Cantidad de decimales.
 * @param {string} simbolo Símbolo de la moneda.
 * @returns {string} El valor formateado.
 */
export function formatoValor(valor, decimales = 2, simbolo = '$') {
    const num = parseFloat(valor);
    if (isNaN(num)) {
        return '-';
    }
    return `${simbolo}${num.toLocaleString('en-US', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })}`;
}

/**
 * Formatea un número como una cantidad de criptomoneda.
 * @param {string|number} valor El número a formatear.
 * @param {number} decimales Cantidad de decimales.
 * @returns {string} La cantidad formateada.
 */
export function formatoCantidad(valor, decimales = 8) {
    const num = parseFloat(valor);
    if (isNaN(num)) {
        return '-';
    }
    return num.toFixed(decimales);
}


// ===> NUEVA FUNCIÓN AÑADIDA <===
/**
 * Formatea números grandes con abreviaturas (M, B, T).
 * @param {string|number} valor El número a formatear.
 * @returns {string} El número abreviado.
 */
export function formatarNumeroGrande(valor) {
    const num = parseFloat(valor);
    if (isNaN(num)) return '-';

    if (num >= 1e12) {
        return `$${(num / 1e12).toFixed(2)}T`;
    }
    if (num >= 1e9) {
        return `$${(num / 1e9).toFixed(2)}B`;
    }
    if (num >= 1e6) {
        return `$${(num / 1e6).toFixed(2)}M`;
    }
    return formatoValor(num, 0);
}


// ===> NUEVA FUNCIÓN AÑADIDA <===
/**
 * Formatea un porcentaje, añadiendo color y una flecha indicadora.
 * @param {string|number} valor El porcentaje a formatear.
 * @returns {string} El HTML con el porcentaje formateado.
 */
export function formatarPorcentajeConColor(valor) {
    const num = parseFloat(valor);
    if (isNaN(num)) return '-';

    const clase = num >= 0 ? 'positivo' : 'negativo';
    const flecha = num >= 0 
        ? '<span class="flecha-verde">▲</span>' 
        : '<span class="flecha-roja">▼</span>';
    
    return `
        <span class="${clase}">
            ${flecha} ${num.toFixed(2)}%
        </span>
    `;
}