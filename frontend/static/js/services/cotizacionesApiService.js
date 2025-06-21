// Este módulo se encarga de toda la comunicación con la API del backend.

/**
 * Obtiene la lista de cotizaciones en formato JSON.
 * @returns {Promise<Array>} Una lista de objetos de cotización.
 */
export async function fetchCotizacionesJSON() {
    try {
        const response = await fetch('/api/cotizaciones');
        if (!response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('❌ Error al obtener los datos de cotizaciones:', error);
        return []; // Devuelve un array vacío en caso de error
    }
}

/**
 * Llama al endpoint que actualiza los datos de cotizaciones en el backend.
 * @returns {Promise<object>} El resultado de la actualización.
 */
export async function triggerActualizacionDatos() {
    try {
        const response = await fetch('/api/actualizar');
        if (!response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('❌ Error al solicitar la actualización de datos:', error);
        return { estado: 'error', mensaje: error.message };
    }
}