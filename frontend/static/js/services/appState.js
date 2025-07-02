/**
 * @file Almacén de estado en memoria para el frontend.
 * @module services/appState
 * @description Este módulo implementa un patrón de estado simple para actuar como la "fuente única de verdad"
 * de la aplicación. Mantiene los datos críticos (criptomonedas, billetera) en un objeto `state` privado
 * y expone un `AppState` con métodos seguros (getters y setters) para interactuar con él.
 */

/**
 * @private
 * @description Contiene el estado de la aplicación. No debe ser modificado directamente desde fuera del módulo.
 * @property {Array<object>} allCryptos - Lista de todas las criptomonedas disponibles en el exchange.
 * @property {Array<object>} ownedCoins - Lista de los activos que el usuario posee en su billetera.
 */
const state = {
    allCryptos: [],
    ownedCoins: []
};

/**
 * @description Objeto singleton que proporciona una interfaz pública para leer y modificar el estado de la aplicación.
 * @namespace AppState
 */
export const AppState = {
    /**
     * Actualiza la lista completa de cotizaciones disponibles en el exchange.
     * @param {Array<object>} cryptos - El nuevo array de criptomonedas.
     * @effects Modifica la propiedad `state.allCryptos`.
     */
    setAllCryptos: (cryptos) => {
        state.allCryptos = cryptos || [];
    },

    /**
     * Actualiza la lista completa de activos en la billetera del usuario.
     * @param {Array<object>} coins - El nuevo array de activos poseídos.
     * @effects Modifica la propiedad `state.ownedCoins`.
     */
    setOwnedCoins: (coins) => {
        state.ownedCoins = coins || [];
    },

    /**
     * Actualiza un único activo en la billetera o lo añade si no existe.
     * @param {object} updatedCoin - El objeto del activo actualizado.
     * @effects Modifica el array `state.ownedCoins`.
     */
    updateSingleOwnedCoin: (updatedCoin) => {
        const index = state.ownedCoins.findIndex(c => c.ticker === updatedCoin.ticker);
        if (index !== -1) {
            state.ownedCoins[index] = updatedCoin;
        } else {
            state.ownedCoins.push(updatedCoin);
        }
    },

    /**
     * Selector que devuelve la lista completa de cotizaciones.
     * @returns {Array<object>} Una copia de la lista de criptomonedas.
     */
    getAllCryptos: () => state.allCryptos,

    /**
     * Selector que devuelve la lista de activos en la billetera.
     * @returns {Array<object>} Una copia de la lista de activos poseídos.
     */
    getOwnedCoins: () => state.ownedCoins,

    /**
     * Selector que busca y devuelve un activo específico de la billetera por su ticker.
     * @param {string} ticker - El ticker del activo a buscar (ej. 'BTC').
     * @returns {object | undefined} El objeto del activo si se encuentra, o `undefined`.
     */
    getOwnedCoinByTicker: (ticker) => {
        return state.ownedCoins.find(coin => coin.ticker === ticker);
    },

    /**
     * Selector que busca y devuelve el precio de una criptomoneda por su ticker.
     * @param {string} ticker - El ticker de la criptomoneda a buscar (ej. 'BTCUSDT').
     * @returns {number | null} El precio como número, o `null` si no se encuentra.
     */
    getPriceByTicker: (ticker) => {
        const crypto = state.allCryptos.find(c => c.ticker === ticker);
        return crypto ? parseFloat(crypto.precio_usd) : null;
    }
};