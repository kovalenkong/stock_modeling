// btn chart download action
btnDownloadChart.onclick = () => {
    let im = mainChart.toBase64Image('image/png', 1)
    let a = document.createElement('a')
    a.href = im
    a.download = 'chart.png'
    a.click()
}
// btn excel download action
btnDownloadExcel.onclick = downloadExcelFile
btnClearForm.onclick = e => {
    e.preventDefault()
    localStorage.removeItem('formFormulaPointRefill')
    localStorage.removeItem('formFormulaOrderSize')
    localStorage.removeItem('formFormulaScore')
    for (let el of form.elements) {
        if (el.name === 'csrfmiddlewaretoken') {
            continue
        }
        el.value = ''
    }
    changeTextLabelForDelayProbability()
}
// btn chart zoom action
btnResetZoom.onclick = () => {
    mainChart.resetZoom()
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
    //pointRadius: 0,
    pointRadius: 2,
    pointHoverRadius: 10,
    backgroundColor: 'rgba(133,192,238, 0.5)',
    borderColor: 'rgb(133,192,238)',
}
const incomeOrderLine = {
    type: 'bar',
    label: 'Приход',
    backgroundColor: '#8bef8b',
    tooltip: {
        callbacks: {
            beforeLabel: function (context) {
                return `Приход №${incomeOrdersCount[context.dataIndex]}`
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
                return `Заявка №${outcomeOrdersCount[context.dataIndex]}`
            }
        }
    }
}
const consumptionLine = {
    label: 'Потребление',
    pointRadius: 0,
    backgroundColor: 'rgba(230,195,250,0.5)',
    borderColor: 'rgb(230,195,250)',
    stepped: 'middle',
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
        }
    }
});


function updateChart(chart, responseDict) {
    let sidebarMenu = document.getElementById('sidebarMenu')
    if (!sidebarMenu.classList.contains('overflow-navbar')) {
        sidebarMenu.classList.add('overflow-navbar')
        //document.body.animate({scrollTop: 1200}, 50)
        //document.body.scrollTop = 0
        window.scroll({
            top: 0,
            behavior: 'smooth'
        });
    }
    chart.data.labels = responseDict['labels']
    infoDiv.innerHTML = responseDict['info']
    btnDownloadChart.disabled = false
    btnDownloadExcel.disabled = false
    btnResetZoom.disabled = false
    let balance_response = responseDict['balance']
    let income_order = responseDict['income_order']
    let outcome_order = responseDict['outcome_order']
    let consumption_response = responseDict['consumption']

    balanceLine.data = balance_response
    consumptionLine.data = consumption_response
    incomeOrderLine.data = income_order
    outcomeOrderLine.data = outcome_order
    /*
    balanceLine.fill = {
        target: 'origin',
        above: '#9ffa9d',
        below: '#ef4f4f'
    }
     */

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
    chart.update()
}

// todo
function downloadExcelFile() {
    let xhr = new XMLHttpRequest()
    xhr.responseType = 'blob'

    xhr.onload = () => {
        if (xhr.status !== 200) {
            console.error(xhr.response)
            showError(`${xhr.status}\n${xhr.responseText}`)
            return
        }
        let file = new Blob([xhr.response], {type: 'application/vnd.ms-excel'})
        let fileUrl = window.URL.createObjectURL(file)
        let a = document.createElement("a");
        a.href = fileUrl;
        a.download = 'res.xlsx';
        a.click()
    }
    xhr.onerror = err => {
        console.error(err)
    }
    xhr.open('POST', '/inventory-models/download')
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.send(JSON.stringify(lastRequestParams))
}