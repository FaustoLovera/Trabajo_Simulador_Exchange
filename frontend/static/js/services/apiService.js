// Centraliza todas las llamadas a la API del backend en un solo lugar.

/**
 * Función genérica para realizar solicitudes fetch a la API.
 * @param {string} url - La URL del endpoint de la API.
 * @param {object} options - Opciones para la solicitud fetch (ej. method, headers, body).
 * @param {string} errorMessage - Mensaje de error personalizado para la excepción.
 * @returns {Promise<any>} - La respuesta JSON de la API.
 * @private
 */
async function _fetchData(url, options = {}, errorMessage = 'Error en la solicitud a la API') {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`${errorMessage} (status: ${response.status})`);
        }
        return await response.json();
    } catch (error) {
        console.error(`❌ Error en la llamada a ${url}:`, error);
        // Re-lanzar el error permite que el código que llama lo maneje (ej. Promise.all).
        throw error;
    }
}

// --- Funciones exportadas para cada endpoint de la API ---

/**
 * Obtiene la lista completa de cotizaciones.
 */
export const fetchCotizaciones = () => 
    _fetchData('/api/cotizaciones', {}, 'No se pudo cargar las cotizaciones');

/**
 * Obtiene el estado completo y formateado de la billetera del usuario.
 */
export const fetchEstadoBilletera = () => 
    _fetchData('/api/billetera/estado-completo', {}, 'No se pudo cargar el estado de la billetera');

/**
 * Obtiene el historial de transacciones del usuario.
 */
export const fetchHistorial = () => 
    _fetchData('/api/historial', {}, 'No se pudo cargar el historial');

/**
 * Obtiene los datos de las velas (candlestick) para el gráfico.
 */
export const fetchVelas = () => 
    _fetchData('/api/velas', {}, 'No se pudo cargar los datos de velas');

/**
 * Solicita al backend que actualice los datos de las cotizaciones desde la fuente externa.
 */
export const triggerActualizacionDatos = () => 
    _fetchData('/api/cotizaciones/actualizar', { method: 'POST' }, 'La solicitud para actualizar datos falló');
