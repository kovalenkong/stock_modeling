

function chartDownloadImage(chart) {
    let im = chart.toBase64Image('image/png', 1)
    let a = document.createElement('a')
    a.href = im
    a.download = 'chart.png'
    a.click()
}

function formClear(form) {
    for (let el of form.elements) {
        if (el.name === 'csrfmiddlewaretoken') {
            continue
        }
        el.value = ''
    }
}

function chartResetZoom(chart) {
    chart.resetZoom()
}

async function changePlaceholder(inputElement, idx, placeholders, playCount) {
    let [placeText, t] = placeholders[idx]
    for (let i = 0; i <= placeText.length; i++) {
        inputElement.placeholder = 'Например: ' + placeText.slice(0, i)
        await sleep(50)
    }
    if (idx + 1 >= placeholders.length) {
        idx = 0
    } else {
        idx++
    }
    await sleep(t)
    for (let i = placeText.length; i >= 0; i--) {
        inputElement.placeholder = 'Например: ' + placeText.slice(0, i)
        await sleep(15)
    }
    if (playCount === 0) {
        inputElement.placeholder = ''
        return
    }
    await changePlaceholder(inputElement, idx, placeholders, playCount - 1)
}

function authorModelPrepareData() {
    let consumptionData = formConsumption.value.replaceAll(',', '.').split('\n').map(Number)
    let data = {
        formula_point_refill: formFormulaPointRefill.value,
        formula_order_size: formFormulaOrderSize.value,
        consumption: consumptionData,
        order_costs: formOrderCosts.value,
        storage_costs: formStorageCosts.value,
        delivery_time: formDeliveryTime.value,
        delay_time: formDelayTime.value,
        initial_stock: formInitialStock.value,
        delay_probability: formDelayProbability.value,
        delay_days: formDelayDays.value.split(',').map(Number),
    }
    if (formFormulaScore.value !== '') {
        data['formula_score'] = formFormulaScore.value
    }
    if (formDeficitLoss.value !== '') {
        data['deficit_losses'] = formDeficitLoss.value
    }
    if (formSInput.value !== '') {
        data['s'] = formSInput.value
    }
    if (formDInput.value !== '') {
        data['d'] = formDInput.value
    }
    return data
}

function buildModelAuthor(data) {
    let xhr = new XMLHttpRequest()
    xhr.onload = () => {
        if (xhr.status !== 200) {
            console.error(xhr.responseText)
            showError(`${xhr.status}\n${xhr.responseText}`)
            return
        }
        return JSON.parse(xhr.response)
        // updateChart(mainChart, resp)  TODO
    }
    xhr.onerror = err => {
        console.error(err)
        showError(`Ошибка сервера\n${xhr.responseText}`)
    }
    xhr.open('POST', '/api/v1/build/author/')
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('X-CSRFToken', form['csrfmiddlewaretoken'].value)
    xhr.send(JSON.stringify(data))
}