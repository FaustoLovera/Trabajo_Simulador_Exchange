/**
 * @file Gestor de datos de la aplicación.
 * @module services/appDataManager
 * @description Este módulo actúa como una capa de orquestación de datos de alto nivel.
 * Es responsable de coordinar las llamadas a `apiService` para obtener datos del backend
 * y de utilizar `appState` para almacenar y gestionar el estado del lado del cliente.
 * Abstrae la lógica de carga inicial, sondeo periódico y acciones de modificación de datos.
 */

import {
    fetchCotizaciones,
    fetchEstadoBilletera,
    fetchHistorial,
    fetchOrdenesAbiertas,
    cancelarOrden
} from './apiService.js';
import { AppState } from './appState.js';

/**
 * @description Objeto singleton que gestiona toda la lógica de datos de la aplicación.
 * @property {function} loadInitialData - Carga todos los datos necesarios para el arranque.
 * @property {function} pollData - Realiza sondeos periódicos para datos dinámicos.
 * @property {function} handleCancelOrder - Gestiona la cancelación de una orden y actualiza el estado.
 */
export const AppDataManager = {
    /**
     * Carga todos los datos iniciales necesarios para la página de trading (bootstrap).
     * Utiliza `Promise.all` para obtener en paralelo cotizaciones, estado de billetera, historial y órdenes.
     * Almacena los datos relevantes en `AppState` y devuelve los necesarios para el renderizado inicial.
     * @async
     * @returns {Promise<{historial: Array<object>, ordenesAbiertas: Array<object>}>} Un objeto con el historial y las órdenes abiertas.
     * @throws {Error} Si alguna de las llamadas a la API falla, el error se propaga para ser manejado por la UI.
     * @effects Modifica `AppState` llamando a `setAllCryptos` y `setOwnedCoins`.
     */
    async loadInitialData() {
        try {
            const [cotizaciones, estadoBilletera, historial, ordenesAbiertas] = await Promise.all([
                fetchCotizaciones(),
                fetchEstadoBilletera(),
                fetchHistorial(),
                fetchOrdenesAbiertas()
            ]);

            AppState.setAllCryptos(cotizaciones);
            AppState.setOwnedCoins(estadoBilletera);

            return { historial, ordenesAbiertas };
        } catch (error) {
            console.error("Error fatal al cargar datos iniciales:", error);
            throw error; // Re-lanzar para que el orquestador de la UI muestre un error crítico.
        }
    },

    /**
     * Realiza un sondeo periódico para actualizar datos dinámicos (estado de billetera y órdenes abiertas).
     * En caso de éxito, actualiza `AppState` y devuelve las nuevas órdenes abiertas para que la UI se refresque.
     * @async
     * @returns {Promise<{nuevasOrdenesAbiertas: Array<object>}|null>} Un objeto con las órdenes actualizadas o `null` si el sondeo falla.
     * @effects Modifica `AppState` llamando a `setOwnedCoins`.
     */
    async pollData() {
        try {
            const [nuevoEstadoBilletera, nuevasOrdenesAbiertas] = await Promise.all([
                fetchEstadoBilletera(),
                fetchOrdenesAbiertas()
            ]);

            AppState.setOwnedCoins(nuevoEstadoBilletera);

            return { nuevasOrdenesAbiertas };
        } catch (error) {
            console.error("Error durante el sondeo de datos. El ciclo continuará:", error);
            return null; // Devolver null para evitar que un fallo en el sondeo rompa la UI.
        }
    },
    
    /**
     * Gestiona la cancelación de una orden. Llama a la API y, si tiene éxito, actualiza el estado
     * del activo correspondiente en `AppState` para reflejar el cambio inmediatamente en la UI.
     * @async
     * @param {string|number} orderId - El ID de la orden a cancelar.
     * @returns {Promise<object>} La respuesta completa de la API tras la cancelación.
     * @effects Puede modificar `AppState` si la cancelación resulta en un activo actualizado.
     */
    async handleCancelOrder(orderId) {
        const respuesta = await cancelarOrden(orderId);
        // Si la API devuelve el estado actualizado del activo, lo actualizamos en el estado local.
        if (respuesta.datos && respuesta.datos.activo_actualizado) {
            const activo = respuesta.datos.activo_actualizado;
            AppState.updateSingleOwnedCoin(activo);
        }
        return respuesta;
    }
};