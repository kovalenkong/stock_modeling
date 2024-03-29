const btnDownloadChart = document.getElementById('btnDownloadChart')
const btnResetZoom = document.getElementById('btnResetZoom')
const btnClearForm = document.getElementById('btnClearForm')
const infoDiv = document.getElementById('infoDiv')


// global state
// для tooltip графика (словарь)
let outcomeOrdersCount
let incomeOrdersCount


// btn chart download action
btnDownloadChart.onclick = () => chartDownloadImage(mainChart)
btnClearForm.onclick = e => {
    e.preventDefault()
    // formClear(form)  // TODO
    changeTextLabelForDelayProbability()
}
// btn chart zoom action
btnResetZoom.onclick = () => chartResetZoom(mainChart)

function chartDownloadImage(chart) {
    let im = chart.toBase64Image('image/png', 1)
    let a = document.createElement('a')
    a.href = im
    a.download = 'chart.png'
    a.click()
}

function chartResetZoom(chart) {
    chart.resetZoom()
}

function updateChart(responseDict) {
    mainChart.data.labels = responseDict['labels']
    infoDiv.innerHTML = responseDict['info']
    btnDownloadChart.disabled = false
    btnResetZoom.disabled = false
    let balance_response = responseDict['balance']
    let income_order = responseDict['income_order']
    let outcome_order = responseDict['outcome_order']
    let consumption_response = responseDict['consumption']

    balanceLine.data = balance_response
    consumptionLine.data = consumption_response
    incomeOrderLine.data = income_order
    outcomeOrderLine.data = outcome_order

    incomeOrdersCount = {}
    let idx = 1
    for (let i = 0; i < income_order.length; i++) {
        if (income_order[i] > 0) {
            incomeOrdersCount[i] = idx
            idx++
        }
    }

    outcomeOrdersCount = {}
    idx = 1
    for (let i = 0; i < outcome_order.length; i++) {
        if (outcome_order[i] > 0) {
            outcomeOrdersCount[i] = idx
            idx++
        }
    }
    mainChart.update()
}

const zoomOptions = {
    pan: {
        enabled: true,
        mode: 'x',
        modifierKey: 'ctrl',
    },
    zoom: {
        drag: {
            enabled: true
        },
        wheel: {
            enabled: true,
        },
        mode: 'x',
    }
}
const balanceLine = {
    label: 'Остаток',
    pointRadius: 2,
    pointHoverRadius: 10,
    backgroundColor: 'rgba(133,192,238, 0.5)',
    borderColor: 'rgba(133,192,238, 0.5)',
    // borderColor: 'rgb(133,192,238)',
}
const incomeOrderLine = {
    type: 'bar',
    label: 'Приход',
    backgroundColor: '#8bef8b',
    tooltip: {
        callbacks: {
            beforeLabel: (ctx) => {
                return `Приход #${incomeOrdersCount[ctx.dataIndex]}`
            },
            label: (ctx) => {
                return `Количество: ${ctx.formattedValue}`
            }
        }
    }
}
const outcomeOrderLine = {
    type: 'bar',
    label: 'Заявка',
    backgroundColor: '#e8ea62',
    tooltip: {
        callbacks: {
            beforeLabel: function (context) {
                return `Заявка #${outcomeOrdersCount[context.dataIndex]}`
            },
            label: (ctx) => {
                return `Количество: ${ctx.formattedValue}`
            }
        }
    }
}
const consumptionLine = {
    label: 'Потребление',
    pointRadius: 0,
    backgroundColor: 'rgba(230,195,250,0.5)',
    borderColor: 'rgba(230,195,250,0.5)',
    // borderColor: 'rgb(230,195,250)',
    stepped: 'middle',
}

const plugin = {
    beforeDraw: (chart) => {
        const {ctx} = chart;
        ctx.save();
        ctx.globalCompositeOperation = 'destination-over';
        ctx.fillStyle = 'rgba(215,212,255,0.1)';

        ctx.fillRect(0, 0, chart.width, chart.height);
        ctx.restore()
    }
}

const chartCtx = document.getElementById('mainChart').getContext('2d');
const mainChart = new Chart(chartCtx, {
    type: 'line',
    labels: [1, 2, 3],
    data: {
        datasets: [
            balanceLine,
            consumptionLine,
            incomeOrderLine,
            outcomeOrderLine,
        ]
    },
    options: {
        animations: {
            radius: {
                duration: 400,
                easing: 'linear',
                loop: (context) => context.active
            }
        },
        plugins: {
            zoom: zoomOptions,
            legend: {
                labels: {
                    color: '#ffffff'
                }
            },
            // TODO tooltip
            // tooltip: {
            //     callbacks: {
            //         title: (ctx) => {
            //             console.log(ctx)
            //             return `День someday`
            //         }
            //     }
            // }
        },
        scales: {
            x: {
                grid: {
                    display: true,
                    drawBorder: true,
                    drawOnChartArea: true,
                    drawTicks: true,
                    lineWidth: 0.3,
                    color: (ctx) => {
                        return '#a1dac1'
                    }
                },

            },
            y: {
                grid: {
                    display: true,
                    drawBorder: true,
                    drawOnChartArea: true,
                    drawTicks: true,
                    lineWidth: 0.3,
                    color: (ctx) => {
                        return '#d4e7dd'
                    }
                },
            }
        },

    },

    plugins: [plugin]
});