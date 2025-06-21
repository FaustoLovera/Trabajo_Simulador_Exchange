/**
 * @module services/apiService
 * @description Centraliza todas las llamadas a la API del backend. Proporciona una función
 * genérica para las solicitudes y exporta funciones específicas para cada endpoint, 
 * manejando errores de forma consistente.
 */

/**
 * Realiza una solicitud `fetch` a un endpoint de la API y maneja la respuesta.
 * @private
 * @async
 * @param {string} url - El endpoint de la API al que se va a llamar.
 * @param {RequestInit} [options={}] - Opciones para la solicitud `fetch` (método, headers, body, etc.).
 * @param {string} [errorMessage='Error en la solicitud a la API'] - Mensaje de error personalizado para lanzar si la respuesta no es `ok`.
 * @returns {Promise<any>} Una promesa que se resuelve con la respuesta JSON de la API.
 * @throws {Error} Lanza un error si la solicitud de red falla o si la respuesta del servidor no es exitosa (status no es 2xx).
 */
async function _fetchData(url, options = {}, errorMessage = 'Error en la solicitud a la API') {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            // Si la respuesta del servidor no es exitosa, construye un error informativo.
            throw new Error(`${errorMessage} (status: ${response.status})`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error en la llamada a la API [${url}]:`, error);
        // Re-lanza el error para que el código que invoca la función pueda manejarlo (ej. en un Promise.all).
        throw error;
    }
}

/**
 * Obtiene la lista completa de cotizaciones de criptomonedas desde el backend.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de objetos de cotización.
 */
export const fetchCotizaciones = () => 
    _fetchData('/api/cotizaciones', {}, 'No se pudieron cargar las cotizaciones');

/**
 * Obtiene el estado completo y formateado de la billetera del usuario.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de objetos, donde cada objeto representa una moneda en la billetera.
 */
export const fetchEstadoBilletera = () => 
    _fetchData('/api/billetera/estado-completo', {}, 'No se pudo cargar el estado de la billetera');

/**
 * Obtiene el historial de transacciones del usuario.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de objetos de transacciones.
 */
export const fetchHistorial = () => 
    _fetchData('/api/historial', {}, 'No se pudo cargar el historial de transacciones');

/**
 * Obtiene los datos de velas (candlestick) para un ticker y un intervalo de tiempo específicos.
 * @param {string} ticker - El ticker de la criptomoneda (ej. 'BTC').
 * @param {string} interval - La temporalidad de las velas (ej. '1d', '1h', '15m').
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de datos de velas.
 */
export const fetchVelas = (ticker, interval) => 
    _fetchData(`/api/velas/${ticker}/${interval}`, {}, `No se pudieron cargar los datos de velas para ${ticker} (${interval})`);

/**
 * Envía una solicitud al backend para que actualice los datos de cotizaciones desde la fuente externa.
 * @returns {Promise<object>} Una promesa que se resuelve con un mensaje de éxito o estado de la actualización.
 */
export const triggerActualizacionDatos = () => 
    _fetchData('/api/actualizar', {}, 'La solicitud para actualizar los datos falló');