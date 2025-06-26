// frontend/static/js/services/apiService.js

/**
 * ### REFACTORIZADO ###
 * Realiza una solicitud `fetch` y maneja respuestas de éxito y de error estructuradas.
 */
async function _fetchData(url, options = {}, errorMessage = 'Error en la solicitud a la API') {
    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            // Si la respuesta no es OK, intentamos leer el cuerpo del error.
            const errorData = await response.json().catch(() => null); // Si el cuerpo no es JSON, devuelve null.
            const message = errorData?.mensaje || response.statusText; // Usa el mensaje del backend o el texto de estado HTTP.
            
            // Creamos un error que contiene los datos estructurados.
            const error = new Error(message);
            error.datos = errorData; // Adjuntamos todos los datos del error.
            error.status = response.status;
            throw error;
        }

        return await response.json();
    } catch (error) {
        console.error(`Error en la llamada a la API [${url}]:`, error);
        throw error; // Re-lanzamos el error para que el código que llama pueda manejarlo.
    }
}

// El resto de las funciones (fetchCotizaciones, fetchEstadoBilletera, etc.) NO CAMBIAN.
// Siguen usando _fetchData, que ahora es más potente.

export const fetchCotizaciones = () => 
    _fetchData('/api/cotizaciones', {}, 'No se pudieron cargar las cotizaciones');

export const fetchEstadoBilletera = () => 
    _fetchData('/api/billetera/estado-completo', {}, 'No se pudo cargar el estado de la billetera');

export const fetchHistorial = () => 
    _fetchData('/api/historial', {}, 'No se pudo cargar el historial de transacciones');

export const fetchVelas = (ticker, interval) => 
    _fetchData(`/api/velas/${ticker}/${interval}`, {}, `No se pudieron cargar los datos de velas para ${ticker} (${interval})`);

export const triggerActualizacionDatos = () => 
    _fetchData('/api/actualizar', {}, 'La solicitud para actualizar los datos falló');

export const fetchComisiones = () => 
    _fetchData('/api/comisiones', {}, 'No se pudo cargar el historial de comisiones');

export const fetchOrdenesAbiertas = () =>
    _fetchData('/api/ordenes-abiertas', {}, 'No se pudo cargar la lista de órdenes abiertas');

export const cancelarOrden = (idOrden) => 
    _fetchData(`/api/orden/cancelar/${idOrden}`, {
        method: 'POST'
    }, 'No se pudo cancelar la orden');