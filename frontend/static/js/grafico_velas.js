console.log('🟢 Script grafico_velas.js cargado');

document.addEventListener('DOMContentLoaded', function () {
    const chartContainer = document.getElementById('chart');

    const chart = window.LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 400,

        layout: {
            textColor: '#0f0f0f', // negro
        },
        grid: {
            vertLines: { color: '#444' },
            horLines: { color: '#444' },
        },
        priceScale: {
            borderColor: '#ffffff',
            ticksVisible: true,
            scaleMargins: {
                top: 0.1,
                bottom: 0.3,
            },
        },
        timeScale: {
            borderColor: '#ffffff',
            timeVisible: true,
            secondsVisible: false,
            ticksVisible: true,
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
    });

    const candleSeries = chart.addCandlestickSeries();

    fetch('/api/velas')
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                console.error('Error del backend:', data.error);
                return;
            }

            const parsedData = data.map((item) => ({
                time: item.time,
                open: Number(item.open),
                high: Number(item.high),
                low: Number(item.low),
                close: Number(item.close),
                volume: Number(item.volume),
            }));

            console.log('Datos recibidos para el gráfico:', parsedData);

            parsedData.forEach((vela, i) => {
                console.log(`Vela ${i + 1}:`, vela);
            });

            candleSeries.setData(parsedData);

            const volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            const volumeData = parsedData.map(vela => ({
                time: vela.time,
                value: vela.volume,
                color: vela.close > vela.open ? '#26a69a' : '#ef5350',
            }));

            volumeSeries.setData(volumeData);

            chart.timeScale().fitContent();
        })
        .catch((error) => {
            console.error('Error al obtener datos:', error);
        });

    new ResizeObserver(() => {
        chart.applyOptions({ width: chartContainer.clientWidth });
    }).observe(chartContainer);
});
