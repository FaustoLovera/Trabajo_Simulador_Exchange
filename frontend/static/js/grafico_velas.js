console.log('🟢 Script grafico_velas.js cargado');

document.addEventListener('DOMContentLoaded', function () {
    const chartContainer = document.getElementById('chart');

    const chart = window.LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: 400,

        // COLORES CLASICOS

        // layout: {
        //     backgroundColor: '#6c757d',
        //     textColor: '#ffffff',
        // },

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
                bottom: 0.1,
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
                time: item.time, // UNIX timestamp en segundos
                open: Number(item.open),
                high: Number(item.high),
                low: Number(item.low),
                close: Number(item.close),
            }));

            console.log('Datos recibidos para el gráfico:', parsedData);

            parsedData.forEach((vela, i) => {
                console.log(`Vela ${i + 1}:`, vela);
            });

            // Añadimos una vela artificial para testeo visual
            parsedData.push({
                time: Math.floor(Date.now() / 1000),
                open: 100,
                high: 120,
                low: 90,
                close: 110,
            });

            candleSeries.setData(parsedData);
            chart.timeScale().fitContent();
        })
        .catch((error) => {
            console.error('Error al obtener datos:', error);
        });

    new ResizeObserver(() => {
        chart.applyOptions({ width: chartContainer.clientWidth });
    }).observe(chartContainer);
});
