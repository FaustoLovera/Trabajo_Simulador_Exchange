// frontend/static/js/services/appDataManager.js

import {
    fetchCotizaciones,
    fetchEstadoBilletera,
    fetchHistorial,
    fetchOrdenesAbiertas,
    cancelarOrden
} from './apiService.js';
import { AppState } from './appState.js';

export const AppDataManager = {
    /**
     * Carga todos los datos iniciales necesarios para la página de trading.
     * Devuelve los datos que son necesarios para el renderizado inicial de la UI.
     */
    async loadInitialData() {
        console.log("Cargando datos iniciales...");
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
            throw error; // Re-lanzar para que el orquestador lo maneje
        }
    },

    /**
     * Realiza un sondeo periódico para actualizar los datos dinámicos.
     * Devuelve los datos que la UI necesita para refrescarse.
     */
    async pollData() {
        console.log("🔄 Realizando sondeo de datos en vivo...");
        try {
            const [nuevoEstadoBilletera, nuevasOrdenesAbiertas] = await Promise.all([
                fetchEstadoBilletera(),
                fetchOrdenesAbiertas()
            ]);

            AppState.setOwnedCoins(nuevoEstadoBilletera);

            return { nuevasOrdenesAbiertas };
        } catch (error) {
            console.error("❌ Error durante el sondeo de datos:", error);
            return null;
        }
    },
    
    /**
     * Gestiona la cancelación de una orden, actualiza el estado y devuelve la respuesta.
     * @param {string} orderId - El ID de la orden a cancelar.
     * @returns {Promise<object>} - La respuesta de la API.
     */
    async handleCancelOrder(orderId) {
        const respuesta = await cancelarOrden(orderId);
        if (respuesta.datos && respuesta.datos.activo_actualizado) {
            const activo = respuesta.datos.activo_actualizado;
            const billeteraActual = AppState.getOwnedCoins();
            const indice = billeteraActual.findIndex(a => a.ticker === activo.ticker);
            if (indice !== -1) {
                billeteraActual[indice] = activo;
                AppState.setOwnedCoins(billeteraActual);
            }
        }
        return respuesta;
    }
};