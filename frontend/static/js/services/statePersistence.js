/**
 * @file Utilitario para la persistencia de estado en el navegador.
 * @module services/statePersistence
 * @description Este módulo proporciona funciones para guardar y cargar de forma segura el estado de la interfaz de usuario
 * en el `localStorage` del navegador. Esto permite que ciertas preferencias del usuario, como el último par
 * de trading visto, persistan entre sesiones y recargas de página.
 */

/**
 * @private
 * @const {string}
 * @description La clave utilizada para almacenar el estado de la vista de trading en `localStorage`.
 * Se usa una constante para evitar errores de tipeo y centralizar el nombre de la clave.
 */
const TRADING_STATE_KEY = 'tradingViewState';

/**
 * Guarda el estado de la vista de trading (ticker e intervalo) en `localStorage`.
 * El objeto de estado se serializa a una cadena JSON antes de ser almacenado.
 * @param {string} ticker - El ticker del par de trading a guardar (ej. 'BTCUSDT').
 * @param {string} interval - El intervalo del gráfico a guardar (ej. '1h').
 * @effects Escribe un valor en `localStorage` bajo la clave `TRADING_STATE_KEY`.
 * @returns {void}
 */
export function saveTradingState(ticker, interval) {
    if (!ticker || !interval) {
        console.warn("Intento de guardar un estado de trading inválido. No se guardó nada.");
        return;
    }
    const state = { ticker, interval };
    try {
        localStorage.setItem(TRADING_STATE_KEY, JSON.stringify(state));
    } catch (error) {
        console.error("Error al guardar el estado en LocalStorage. El almacenamiento puede estar lleno o deshabilitado.", error);
    }
}

/**
 * Carga el estado de la vista de trading desde `localStorage`.
 * Intenta leer y deserializar el estado guardado. Si no existe o hay un error, devuelve `null`.
 * @returns {{ticker: string, interval: string} | null} Un objeto con el ticker y el intervalo guardados,
 * o `null` si no se encuentra ningún estado válido o si ocurre un error.
 */
export function loadTradingState() {
    try {
        const savedStateJSON = localStorage.getItem(TRADING_STATE_KEY);
        if (savedStateJSON) {
            return JSON.parse(savedStateJSON);
        }
        return null; // No hay estado guardado, es un caso de uso normal.
    } catch (error) {
        console.error("Error al cargar o parsear el estado desde LocalStorage. Se devolverá null.", error);
        return null; // Si los datos están corruptos, es más seguro no devolver nada.
    }
}