/**
 * Busca los datos de las velas en la API.
 * @returns {Promise<Array>}
 */
async function fetchVelasData() {
    try {
        const response = await fetch('/api/velas');
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('❌ Error al obtener los datos de las velas:', error);
        return [];
    }
}

/**
 * Inicializa y renderiza el gráfico de velas en el contenedor especificado.
 */
export async function initializeChart() {
    console.log('📈 Inicializando gráfico de velas...');
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) {
        console.warn("Elemento #chart no encontrado. No se puede renderizar el gráfico.");
        return;
    }

    if (!window.LightweightCharts) {
        console.error("La librería LightweightCharts no está cargada. Asegúrate de que se carga antes que este script.");
        return;
    }

    const chart = window.LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 500,
        layout: { textColor: '#ccc', background: { type: 'solid', color: '#1E1E1E' } },
        grid: { vertLines: { color: '#2B2B2B' }, horzLines: { color: '#2B2B2B' } },
        priceScale: { borderColor: '#485c7b' },
        timeScale: { borderColor: '#485c7b' },
    });

    const candleSeries = chart.addCandlestickSeries({
        upColor: 'rgb(31, 191, 113)',
        downColor: 'rgb(226, 33, 52)',
        borderDownColor: 'rgb(226, 33, 52)',
        borderUpColor: 'rgb(31, 191, 113)',
        wickDownColor: '#838ca1',
        wickUpColor: '#838ca1',
    });

    const volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '',
    });
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

    const data = await fetchVelasData();
    if (data.length > 0) {
        const candleData = data.map(item => ({
            time: item.time, open: Number(item.open), high: Number(item.high), low: Number(item.low), close: Number(item.close)
        }));
        const volumeData = data.map(item => ({
            time: item.time, value: Number(item.volume), color: Number(item.close) > Number(item.open) ? 'rgba(31, 191, 113, 0.5)' : 'rgba(226, 33, 52, 0.5)'
        }));
        candleSeries.setData(candleData);
        volumeSeries.setData(volumeData);
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