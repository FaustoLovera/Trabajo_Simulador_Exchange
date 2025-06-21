/**
 * @module chartRenderer
 * @description Gestiona la creación, inicialización y actualización del gráfico financiero
 * de velas utilizando la biblioteca Lightweight Charts™.
 * Este módulo es responsable de todas las interacciones directas con la instancia del gráfico.
 */

// Variables globales para mantener las instancias del gráfico y sus series.
let chart;
let candleSeries;
let volumeSeries;

/**
 * @typedef {object} CandleData
 * @property {string} time - Marca de tiempo en formato 'YYYY-MM-DD'.
 * @property {number} open - Precio de apertura.
 * @property {number} high - Precio máximo.
 * @property {number} low - Precio mínimo.
 * @property {number} close - Precio de cierre.
 * @property {number} volume - Volumen de la operación.
 */

/**
 * Crea e inicializa el gráfico de velas en la primera carga.
 * Configura la apariencia del gráfico, añade las series de velas y volumen,
 * y establece los listeners de eventos para la interactividad.
 *
 * @param {CandleData[]} initialData - El conjunto de datos inicial de velas para mostrar.
 * @side-effects Manipula el DOM para crear el gráfico dentro del elemento '#chart'.
 *               También adjunta un ResizeObserver para manejar el redimensionamiento responsivo.
 */
export function initializeChart(initialData) {
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) {
        console.warn("Elemento #chart no encontrado. No se puede renderizar el gráfico.");
        return;
    }
    if (!window.LightweightCharts) {
        console.error("La biblioteca LightweightCharts no está cargada.");
        return;
    }

    // Crea la instancia principal del gráfico con estilos personalizados.
    chart = window.LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 500,
        layout: { textColor: '#ccc', background: { type: 'solid', color: '#1E1E1E' } },
        grid: { vertLines: { color: '#2B2B2B' }, horzLines: { color: '#2B2B2B' } },
        priceScale: { borderColor: '#485c7b' },
        timeScale: { borderColor: '#485c7b' },
    });

    // Añade la serie principal de velas para la acción del precio.
    candleSeries = chart.addCandlestickSeries({
        upColor: 'rgb(31, 191, 113)',
        downColor: 'rgb(226, 33, 52)',
        borderDownColor: 'rgb(226, 33, 52)',
        borderUpColor: 'rgb(31, 191, 113)',
        wickDownColor: '#838ca1',
        wickUpColor: '#838ca1',
    });

    // Añade una serie secundaria de histograma para el volumen de operaciones.
    volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '', // Se adjunta a una escala de precios separada.
    });
    // Ajusta la escala de precios de la serie de volumen para darle más espacio.
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

    if (initialData && initialData.length > 0) {
        updateChartData(initialData);
    }

    // Añade un listener de eventos al checkbox para alternar la visibilidad del volumen.
    const volumeCheckbox = document.getElementById('toggleVolume');
    if (volumeCheckbox) {
        volumeCheckbox.addEventListener('change', (e) => {
            volumeSeries.applyOptions({ visible: e.target.checked });
        });
    }

    // Asegura que el gráfico se ajuste a su contenido y sea responsivo.
    chart.timeScale().fitContent();
    new ResizeObserver(() => chart.applyOptions({ width: chartContainer.clientWidth })).observe(chartContainer);
}

/**
 * Actualiza el gráfico con un nuevo conjunto de datos de velas.
 * Maneja tanto el caso en que hay datos disponibles como en el que no, mostrando
 * u ocultando un mensaje de error superpuesto según corresponda.
 *
 * @param {CandleData[]} data - El nuevo array de datos de velas. Si el array está vacío
 *        o es nulo, limpia el gráfico y muestra un mensaje de error.
 */
export function updateChartData(data) {
    if (!candleSeries || !volumeSeries) {
        console.warn("El gráfico no está inicializado. No se pueden actualizar los datos.");
        return;
    }

    const errorOverlay = document.getElementById('chart-error-overlay');

    if (data && data.length > 0) {
        // Oculta el mensaje de error si hay datos disponibles.
        errorOverlay.style.display = 'none';

        // Mapea los datos brutos al formato requerido por Lightweight Charts.
        const candleData = data.map(item => ({
            time: item.time,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close)
        }));
        const volumeData = data.map(item => ({
            time: item.time,
            value: Number(item.volume),
            color: Number(item.close) > Number(item.open) ? 'rgba(31, 191, 113, 0.5)' : 'rgba(226, 33, 52, 0.5)'
        }));

        console.log(`📊 Actualizando gráfico con ${data.length} velas.`);
        candleSeries.setData(candleData);
        volumeSeries.setData(volumeData);
    } else {
        // Si no hay datos disponibles, limpia las series y muestra el overlay de error.
        console.log("📊 No hay datos de velas disponibles. Mostrando mensaje de error.");
        candleSeries.setData([]);
        volumeSeries.setData([]);
        errorOverlay.style.display = 'flex'; // Se usa 'flex' para que coincida con el centrado del CSS.
    }
}