/**
 * @file Capa de servicio para la comunicación con la API del backend.
 * @module services/apiService
 * @description Este módulo centraliza todas las llamadas `fetch` al backend. Proporciona una
 * función de ayuda `_fetchData` que estandariza el manejo de respuestas y errores, y exporta
 * una función específica para cada endpoint de la API, definiendo así un contrato claro
 * entre el frontend y el backend.
 */

/**
 * @private
 * @async
 * @function _fetchData
 * @description Realiza una solicitud `fetch` genérica y maneja las respuestas.
 * Si la respuesta es exitosa (response.ok), devuelve el cuerpo de la respuesta en formato JSON.
 * Si la respuesta indica un error, intenta parsear el cuerpo del error JSON del backend
 * y lanza un error estructurado que contiene el mensaje, el estado y los datos del error.
 * @param {string} url - La URL del endpoint de la API a la que se va a solicitar.
 * @param {object} [options={}] - El objeto de opciones para la solicitud `fetch` (método, headers, body, etc.).
 * @returns {Promise<any>} Una promesa que se resuelve con los datos de la respuesta en formato JSON.
 * @throws {Error} Lanza un error si la solicitud de red falla o si el servidor devuelve un estado de error.
 * El objeto de error puede contener `datos` y `status` con información adicional del backend.
 */
async function _fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            const message = errorData?.mensaje || response.statusText;
            
            const error = new Error(message);
            error.datos = errorData;
            error.status = response.status;
            throw error;
        }

        return await response.json();
    } catch (error) {
        // El error ya fue procesado o es un error de red. Lo relanzamos para que sea manejado por la capa superior.
        throw error;
    }
}

/**
 * Obtiene la lista completa de cotizaciones de mercado.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de objetos de cotización.
 * @throws {Error} Si la solicitud a `GET /api/cotizaciones` falla.
 */
export const fetchCotizaciones = () => _fetchData('/api/cotizaciones');

/**
 * Obtiene el estado completo y detallado de la billetera del usuario.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de activos en la billetera.
 * @throws {Error} Si la solicitud a `GET /api/billetera/estado-completo` falla.
 */
export const fetchEstadoBilletera = () => _fetchData('/api/billetera/estado-completo');

/**
 * Obtiene el historial de transacciones (órdenes ejecutadas).
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de transacciones.
 * @throws {Error} Si la solicitud a `GET /api/historial` falla.
 */
export const fetchHistorial = () => _fetchData('/api/historial');

/**
 * Obtiene los datos de velas (OHLCV) para un par de trading y un intervalo específicos.
 * @param {string} ticker - El par de trading (ej. 'BTCUSDT').
 * @param {string} interval - El intervalo de tiempo de las velas (ej. '1h', '1d').
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de datos de velas.
 * @throws {Error} Si la solicitud a `GET /api/velas/{ticker}/{interval}` falla.
 */
export const fetchVelas = (ticker, interval) => _fetchData(`/api/velas/${ticker}/${interval}`);

/**
 * Solicita al backend que actualice sus datos de mercado desde la fuente externa.
 * @returns {Promise<object>} Una promesa que se resuelve con un mensaje de éxito.
 * @throws {Error} Si la solicitud a `GET /api/actualizar` falla.
 */
export const triggerActualizacionDatos = () => _fetchData('/api/actualizar');

/**
 * Obtiene el historial de comisiones pagadas.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de registros de comisiones.
 * @throws {Error} Si la solicitud a `GET /api/comisiones` falla.
 */
export const fetchComisiones = () => _fetchData('/api/comisiones');

/**
 * Obtiene la lista de órdenes de trading que están actualmente abiertas.
 * @returns {Promise<Array<object>>} Una promesa que se resuelve con un array de órdenes abiertas.
 * @throws {Error} Si la solicitud a `GET /api/ordenes-abiertas` falla.
 */
export const fetchOrdenesAbiertas = () => _fetchData('/api/ordenes-abiertas');

/**
 * Envía una solicitud para cancelar una orden de trading abierta.
 * @param {string|number} idOrden - El ID de la orden que se desea cancelar.
 * @returns {Promise<object>} Una promesa que se resuelve con un mensaje de confirmación.
 * @throws {Error} Si la solicitud a `POST /api/orden/cancelar/{idOrden}` falla.
 */
export const cancelarOrden = (idOrden) => 
    _fetchData(`/api/orden/cancelar/${idOrden}`, { method: 'POST' });