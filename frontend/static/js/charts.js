    /**
     * HealthAnalytics IPS — Chart Utilities
     * Funciones reutilizables para Chart.js
     */

    const HA_COLORS = {
        primary:  '#0066CC',
        accent:   '#00A3E0',
        success:  '#00875A',
        warning:  '#FF8B00',
        danger:   '#DE350B',
        purple:   '#6554C0',
        pink:     '#FF5630',
        teal:     '#00B8D9',
        gray:     '#6B778C',
        lightGray:'#DFE1E6',
    };

    const RISK_COLORS = {
        'Bajo':    '#00875A',
        'Medio':   '#FF8B00',
        'Alto':    '#FF5630',
        'Crítico': '#DE350B',
    };

    const CHART_DEFAULTS = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: { family: 'Inter, sans-serif', size: 12 },
                    color: '#172B4D',
                    padding: 16,
                }
            },
            tooltip: {
                backgroundColor: '#172B4D',
                titleFont: { family: 'Inter, sans-serif', size: 12 },
                bodyFont:  { family: 'Inter, sans-serif', size: 12 },
                padding: 10,
                cornerRadius: 8,
            }
        }
    };

    /**
     * Gráfica de TORTA — distribución de riesgo
     */
    function buildRiesgoChart(canvasId, distribucion) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const labels = Object.keys(distribucion);
        const values = Object.values(distribucion);
        const colors = labels.map(l => RISK_COLORS[l] || HA_COLORS.gray);

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 6,
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                cutout: '65%',
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' }
                }
            }
        });
    }

    /**
     * Gráfica de BARRAS APILADAS — riesgo por grupo de edad
     */
    function buildEdadRiesgoChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const labels = data.map(d => d.grupo_edad);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Bajo',    data: data.map(d => d.bajo),    backgroundColor: RISK_COLORS['Bajo']    + 'CC' },
                    { label: 'Medio',   data: data.map(d => d.medio),   backgroundColor: RISK_COLORS['Medio']   + 'CC' },
                    { label: 'Alto',    data: data.map(d => d.alto),    backgroundColor: RISK_COLORS['Alto']    + 'CC' },
                    { label: 'Crítico', data: data.map(d => d.critico), backgroundColor: RISK_COLORS['Crítico'] + 'CC' },
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 11 } } },
                    y: { stacked: true, grid: { color: '#EEF2F7' }, ticks: { font: { size: 11 } } }
                },
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' }
                }
            }
        });
    }

    /**
     * Gráfica de BARRAS — distribución por sexo
     */
    function buildSexoChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const labels = data.map(d => d.sexo === 'M' ? 'Masculino' : 'Femenino');

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Total',       data: data.map(d => d.total),       backgroundColor: HA_COLORS.primary  + 'BB' },
                    { label: 'Críticos',    data: data.map(d => d.criticos),    backgroundColor: RISK_COLORS['Crítico'] + 'BB' },
                    { label: 'Hipertensos', data: data.map(d => d.hipertensos), backgroundColor: HA_COLORS.warning  + 'BB' },
                    { label: 'Diabéticos',  data: data.map(d => d.diabeticos),  backgroundColor: HA_COLORS.purple   + 'BB' },
                ]
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: '#EEF2F7' } }
                }
            }
        });
    }

    /**
     * Gráfica de TORTA — distribución por IMC
     */
    function buildImcChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const IMC_COLORS = {
            'Bajo peso':  '#00B8D9',
            'Normal':     '#00875A',
            'Sobrepeso':  '#FF8B00',
            'Obesidad':   '#DE350B',
        };

        const labels = data.map(d => d.imc_clasificacion || 'Sin datos');
        const values = data.map(d => d.total);
        const colors = labels.map(l => IMC_COLORS[l] || HA_COLORS.gray);

        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' }
                }
            }
        });
    }

    /**
     * Gráfica de LÍNEA — tendencia temporal
     */
    function buildLineChart(canvasId, labels, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: datasets.map((ds, i) => ({
                    ...ds,
                    borderWidth: 2,
                    pointRadius: 4,
                    tension: 0.3,
                    fill: false,
                    borderColor: ds.color || Object.values(HA_COLORS)[i],
                    pointBackgroundColor: ds.color || Object.values(HA_COLORS)[i],
                }))
            },
            options: {
                ...CHART_DEFAULTS,
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: '#EEF2F7' } }
                }
            }
        });
    }

    /**
     * Gráfica de BARRAS HORIZONTALES — feature importance ML
     */
    function buildFeatureImportanceChart(canvasId, featureData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const sorted = Object.entries(featureData).sort((a, b) => b[1] - a[1]);
        const labels = sorted.map(([k]) => k);
        const values = sorted.map(([, v]) => +(v * 100).toFixed(2));

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Importancia (%)',
                    data: values,
                    backgroundColor: values.map((_, i) =>
                        `hsl(${210 + i * 15}, 70%, ${55 - i * 3}%)`
                    ),
                    borderRadius: 6,
                }]
            },
            options: {
                ...CHART_DEFAULTS,
                indexAxis: 'y',
                scales: {
                    x: { grid: { color: '#EEF2F7' }, ticks: { callback: v => v + '%' } },
                    y: { grid: { display: false } }
                },
                plugins: {
                    ...CHART_DEFAULTS.plugins,
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Destruye un chart si ya existe (para evitar duplicados al recargar)
     */
    function destroyChart(chartInstance) {
        if (chartInstance) {
            chartInstance.destroy();
        }
        return null;
    }