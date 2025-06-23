/**
 * @module services/appState
 * @description Centraliza el estado de la aplicación para evitar el uso de variables globales.
 * Proporciona métodos seguros para leer y escribir en el estado.
 */

const state = {
    allCryptos: [],
    ownedCoins: []
};

export const AppState = {
    /**
     * Establece la lista completa de cotizaciones.
     * @param {Array<object>} cryptos - La lista de criptomonedas.
     */
    setAllCryptos: (cryptos) => {
        state.allCryptos = cryptos || [];
    },

    /**
     * Establece la lista de monedas que el usuario posee.
     * @param {Array<object>} coins - La lista de monedas en la billetera.
     */
    setOwnedCoins: (coins) => {
        state.ownedCoins = coins || [];
    },

    /**
     * Obtiene la lista completa de cotizaciones.
     * @returns {Array<object>}
     */
    getAllCryptos: () => state.allCryptos,

    /**
     * Obtiene la lista de monedas que el usuario posee.
     * @returns {Array<object>}
     */
    getOwnedCoins: () => state.ownedCoins,

    /**
     * Busca una moneda específica que el usuario posee por su ticker.
     * @param {string} ticker - El ticker de la moneda.
     * @returns {object | undefined} El objeto de la moneda o undefined si no se encuentra.
     */
    getOwnedCoinByTicker: (ticker) => {
        return state.ownedCoins.find(coin => coin.ticker === ticker);
    }
};