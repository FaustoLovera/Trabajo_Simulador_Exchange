/**
 * @module services/statePersistence
 * @description Gestiona el guardado y la carga del estado de la aplicación
 * en el Almacenamiento Local (LocalStorage) del navegador.
 */

// Usamos una clave constante para evitar errores de tipeo.
const TRADING_STATE_KEY = 'tradingViewState';

/**
 * Guarda el estado actual de la vista de trading (ticker e intervalo).
 * @param {string} ticker - El ticker de la criptomoneda actual.
 * @param {string} interval - El intervalo de tiempo actual.
 */
export function saveTradingState(ticker, interval) {
    if (!ticker || !interval) {
        console.warn("Intento de guardar estado de trading inválido.");
        return;
    }
    const state = { ticker, interval };
    try {
        // Los objetos deben ser convertidos a string (JSON) para guardarse en LocalStorage.
        localStorage.setItem(TRADING_STATE_KEY, JSON.stringify(state));
    } catch (error) {
        console.error("Error al guardar el estado en LocalStorage:", error);
    }
}

/**
 * Carga el estado de la vista de trading desde LocalStorage.
 * @returns {{ticker: string, interval: string} | null} El estado guardado o null si no se encuentra nada.
 */
export function loadTradingState() {
    try {
        const savedStateJSON = localStorage.getItem(TRADING_STATE_KEY);
        if (savedStateJSON) {
            // Si encontramos datos, los convertimos de nuevo a un objeto JavaScript.
            return JSON.parse(savedStateJSON);
        }
        return null; // No hay estado guardado.
    } catch (error) {
        console.error("Error al cargar el estado desde LocalStorage:", error);
        return null;
    }
}