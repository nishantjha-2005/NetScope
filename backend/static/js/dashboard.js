
const chartElement = document.getElementById(
    'performanceChart'
);

if (chartElement) {

    const labels = JSON.parse(
        document.getElementById('chart-labels').textContent
    );

    const values = JSON.parse(
        document.getElementById('chart-values').textContent
    );

    new Chart(chartElement, {
        type: 'line',

        data: {
            labels: labels,

            datasets: [{
                label: 'Page Load Time (seconds)',

                data: values,

                borderWidth: 2,
                tension: 0.3,
                fill: false
            }]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    display: true
                }
            },

            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Seconds'
                    }
                }
            }
        }
    });
}
