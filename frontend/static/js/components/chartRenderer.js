// frontend/static/js/components/chartRenderer.js

let chart;
let candleSeries;
let volumeSeries;

/**
 * Crea e inicializa el gráfico de velas la primera vez.
 * @param {Array} initialData - Los datos iniciales para mostrar.
 */
export function initializeChart(initialData) {
    console.log('📈 Initializing candlestick chart...');
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) {
        console.warn("Element #chart not found. Cannot render chart.");
        return;
    }
    if (!window.LightweightCharts) {
        console.error("LightweightCharts library is not loaded.");
        return;
    }

    chart = window.LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 500,
        layout: { textColor: '#ccc', background: { type: 'solid', color: '#1E1E1E' } },
        grid: { vertLines: { color: '#2B2B2B' }, horzLines: { color: '#2B2B2B' } },
        priceScale: { borderColor: '#485c7b' },
        timeScale: { borderColor: '#485c7b' },
    });

    candleSeries = chart.addCandlestickSeries({
        upColor: 'rgb(31, 191, 113)',
        downColor: 'rgb(226, 33, 52)',
        borderDownColor: 'rgb(226, 33, 52)',
        borderUpColor: 'rgb(31, 191, 113)',
        wickDownColor: '#838ca1',
        wickUpColor: '#838ca1',
    });

    volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '',
    });
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

    if (initialData && initialData.length > 0) {
        updateChartData(initialData);
    }
    
    const volumeCheckbox = document.getElementById('toggleVolume');
    if (volumeCheckbox) {
        volumeCheckbox.addEventListener('change', (e) => {
            volumeSeries.applyOptions({ visible: e.target.checked });
        });
    }

    chart.timeScale().fitContent();
    new ResizeObserver(() => chart.applyOptions({ width: chartContainer.clientWidth })).observe(chartContainer);
}

/**
 * Actualiza el gráfico con nuevos datos y controla la visibilidad del overlay de error.
 * @param {Array} data - Los nuevos datos de velas.
 */
export function updateChartData(data) {
    if (!candleSeries || !volumeSeries) {
        console.warn("El gráfico no está inicializado.");
        return;
    }

    // Obtenemos una referencia a nuestro nuevo div de error.
    const errorOverlay = document.getElementById('chart-error-overlay');

    if (data && data.length > 0) {
        // Si hay datos, nos aseguramos de que el overlay esté oculto.
        errorOverlay.style.display = 'none';

        const candleData = data.map(item => ({
            time: item.time, open: Number(item.open), high: Number(item.high), low: Number(item.low), close: Number(item.close)
        }));
        const volumeData = data.map(item => ({
            time: item.time, value: Number(item.volume), color: Number(item.close) > Number(item.open) ? 'rgba(31, 191, 113, 0.5)' : 'rgba(226, 33, 52, 0.5)'
        }));
        
        console.log(`📊 Actualizando gráfico con ${data.length} nuevas velas.`);
        candleSeries.setData(candleData);
        volumeSeries.setData(volumeData);
    } else {
        // Si NO hay datos, limpiamos las series y MOSTRAMOS el overlay.
        console.log("📊 No hay datos de velas disponibles. Mostrando mensaje de error.");
        candleSeries.setData([]);
        volumeSeries.setData([]);
        errorOverlay.style.display = 'flex'; // Usamos 'flex' porque así lo centramos en el CSS.
    }
}