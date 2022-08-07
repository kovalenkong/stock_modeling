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

// datasets modal
const modalListDatasets = document.getElementById('listDatasets')
const listDatasetsTableBody = document.getElementById('listDatasetsTableBody')
modalListDatasets.addEventListener('shown.bs.modal', () => {
    let xhr = new XMLHttpRequest()
    xhr.onload = () => {
        listDatasetsTableBody.textContent = ''
        let response = JSON.parse(xhr.response)
        for (let row of response) {
            let el = document.createElement('tr')

            let id = document.createElement('td')
            id.textContent = row['id']
            let dtCreated = document.createElement('td')
            dtCreated.textContent = row['dt_created']
            let dtEdited = document.createElement('td')
            dtEdited.textContent = row['dt_edited']
            let author = document.createElement('td')
            author.textContent = row['author']['email']

            let d = document.createElement('div')
            d.className = 'btn-group'
            let dropdownBtn = document.createElement('button')
            dropdownBtn.textContent = 'Выбрать'
            dropdownBtn.className = 'btn btn-outline-primary dropdown-toggle'
            dropdownBtn.setAttribute('data-bs-toggle', 'dropdown')
            dropdownBtn.setAttribute('area-expanded', 'false')
            d.appendChild(dropdownBtn)

            let dropDownMenu = document.createElement('ul')
            dropDownMenu.className = 'dropdown-menu'
            d.appendChild(dropDownMenu)
            let btnChooseDatasetOnly = document.createElement('button')
            btnChooseDatasetOnly.textContent = 'Только потребление'
            btnChooseDatasetOnly.className = 'dropdown-item'
            btnChooseDatasetOnly.onclick = e => {
                let xhr = new XMLHttpRequest()
                xhr.onload = () => {
                    let resp = JSON.parse(xhr.response)
                    console.log(resp)
                    formConsumption.value = resp['data']
                    $('#listDatasets').modal('hide')
                }
                xhr.onerror = err => {
                    console.error(err)
                }
                xhr.open('GET', `/api/v1/datasets/${row['id']}`)
                xhr.send()
            }
            let btnChooseDatasetWithParameters = document.createElement('button')
            btnChooseDatasetWithParameters.textContent = 'Потребление и параметры'
            btnChooseDatasetWithParameters.className = 'dropdown-item disabled'
            btnChooseDatasetWithParameters.onclick = e => {
                let xhr = new XMLHttpRequest()
                xhr.onload = () => {
                    let resp = JSON.parse(xhr.response)
                    let params = JSON.parse(resp.parameters)
                    // TODO
                    console.log(params)
                    if (params['avg_daily_consumption'] !== null) {
                        formSInput.value = params['avg_daily_consumption']
                    }
                    if (params['avg_daily_consumption_d'] !== null) {
                        formDInput.value = params['avg_daily_consumption_d']
                    }
                    if (params['deficit_losses'] !== null) {
                        formDeficitLoss.value = params['deficit_losses']
                    }
                    if (params['delay_days'] !== null) {
                        formDelayDays.value = params['delay_days']
                    }
                    if (resp['data'] !== null) {
                        formConsumption.value = resp['data']
                    }
                    if (params['delay_probability'] !== null) {
                        formDelayProbability.value = params['delay_probability']
                    }
                    if (params['delay_time'] !== null) {
                        formDelayTime.value = params['delay_time']
                    }
                    if (params['delivery_time'] !== null) {
                        formDeliveryTime.value = params['delivery_time']
                    }
                    if (params['initial_stock'] !== null) {
                        formInitialStock.value = params['initial_stock']
                    }
                    if (params['order_costs'] !== null) {
                        formOrderCosts.value = params['order_costs']
                    }
                    if (params['storage_costs'] !== null) {
                        formStorageCosts.value = params['storage_costs']
                    }
                    $('#listDatasets').modal('hide')
                }
                xhr.onerror = err => {
                    console.error(err)
                }
                xhr.open('GET', `/api/v1/datasets/${row['id']}`)
                xhr.send()
            }
            dropDownMenu.appendChild(document.createElement('li').appendChild(btnChooseDatasetOnly))
            dropDownMenu.appendChild(document.createElement('li').appendChild(btnChooseDatasetWithParameters))

            let tdAction = document.createElement('td')
            tdAction.appendChild(d)

            el.appendChild(id)
            el.appendChild(dtCreated)
            el.appendChild(dtEdited)
            el.appendChild(author)
            el.appendChild(tdAction)
            listDatasetsTableBody.appendChild(el)
        }
        console.log(xhr.response)
    }
    xhr.onerror = err => {
        console.error(err)
    }
    xhr.open('get', '/api/v1/datasets/')
    xhr.send()
})

// form elements
      const form = document.getElementsByTagName('form')[0]

      const formFormulaPointRefill = document.getElementById('formulaPointRefill')
      const formFormulaOrderSize = document.getElementById('formulaOrderSize')
      const formFormulaScore = document.getElementById('formulaScore')
      const formFormulaIsPublic = document.getElementById('formFormulaIsPublic')
      const formFormulaDescription = document.getElementById('formFormulaDescription')

      const formOrderCosts = document.getElementById('orderCosts')
      const formStorageCosts = document.getElementById('storageCosts')
      const formDeliveryTime = document.getElementById('deliveryTime')
      const formDelayTime = document.getElementById('delayTime')
      const formInitialStock = document.getElementById('initialStock')
      const formDelayProbability = document.getElementById('delayProbability')
      const formDelayDays = document.getElementById('delayDays')
      // optional form fields
      const formDeficitLoss = document.getElementById('deficitLosses')
      const formDInput = document.getElementById('avgDailyConsumption')
      const formSInput = document.getElementById('avgDailyConsumptionD')
      const formConsumption = document.getElementById('consumptionDataset')

      // работа с графиком
      const btnDownloadChart = document.getElementById('btnDownloadChart')
      const btnResetZoom = document.getElementById('btnResetZoom')
      const btnDownloadExcel = document.getElementById('btnDownloadExcel')
      const btnClearForm = document.getElementById('btnClearForm')
      const infoDiv = document.getElementById('infoDiv')
      const btnSaveAlgorithm = document.getElementById('btnSaveAlgorithm')
      const btnSaveAlgorithmBefore = document.getElementById('btnSaveAlgorithmBefore')


      function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms))
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

      changePlaceholder(
          formFormulaPointRefill,
          0,
          [
              ['curBalance < 1000', 2000],
              ['iDay % 5 == 0', 4000],
              ['curBalance <= MEAN(Consumption) * (Delivery + Delay)', 5000],
              ['(iDay % 3 == 0) OR (balance < 1000)', 5000],
          ],
          5
      )
      changePlaceholder(
          formFormulaOrderSize,
          0,
          [
              ['ABS(curBalance) * 3', 2000],
              ['MEAN(Consumption) * (Delivery + Delay)', 3000],
              ['Consumption[iDay-(Delivery+Delay):iDay]', 5000],
          ],
          5
      )


      // для tooltip графика (словарь)
      let outcomeOrdersCount
      let incomeOrdersCount
      // для загрузки
      let lastRequestParams

      const consumptionRegex = /^(\d+[.,]?\d*\n)*\d+.?\d*$/

      form.onsubmit = e => {
          e.preventDefault()
          if (!form.checkValidity()) {
              return
          }
          if (!consumptionRegex.test(formConsumption.value)) {
              showError('Заполните данные потребления в указанном формате\n' +
                  'Каждое значение с новой строки, разделитель точка или запятая')
              return
          }
          buildModelAuthor()
      }

      // delay probability events
      formDelayProbability.oninput = changeTextLabelForDelayProbability
      changeTextLabelForDelayProbability()

      function changeTextLabelForDelayProbability() {
          formDelayProbability.labels[0].textContent = `Вероятность задержки: ${Math.round(formDelayProbability.value * 100).toFixed(0)}%`
      }

      // delay days field changes
      formDelayDays.oninput = e => {
          e.preventDefault()
          if (formDelayDays.value !== '') {
              formDelayProbability.value = 0
              changeTextLabelForDelayProbability()
          }
          formDelayProbability.disabled = formDelayDays.value !== '';
      }

      function buildModelAuthor() {
          let consumptionData = formConsumption.value.replaceAll(',', '.').split('\n').map(Number)

          let xhr = new XMLHttpRequest()
          xhr.onload = () => {
              if (xhr.status !== 200) {
                  console.error(xhr.responseText)
                  showError(`${xhr.status}\n${xhr.responseText}`)
                  return
              }
              let resp = JSON.parse(xhr.response)
              updateChart(mainChart, resp)
          }
          xhr.onerror = err => {
              console.error(err)
              showError(`Ошибка сервера\n${xhr.responseText}`)
          }
          xhr.open('POST', '/api/v1/build/author/')
          xhr.setRequestHeader('Content-Type', 'application/json')
          xhr.setRequestHeader('X-CSRFToken', form['csrfmiddlewaretoken'].value)
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
          lastRequestParams = data
          xhr.send(JSON.stringify(data))
      }

      // работа с сохранением алгоритма
      let algorithmID = '{{ form_algo.instance.id|default:"" }}'

      btnSaveAlgorithmBefore.onclick = e => {
          e.preventDefault()
          if (!checkAlgorithmFormValid()) {
              return
          }
          $('#modalSaveAlgorithm').modal('show')
      }
      btnSaveAlgorithm.onclick = e => {
          e.preventDefault()
          if (!checkAlgorithmFormValid()) {
              return
          }
          if (algorithmID === '') {
              algorithmSaveNew()
          } else {
              algorithmUpdate()
          }
          $('#modalSaveAlgorithm').modal('hide')
      }

      function checkAlgorithmFormValid() {
          let requiredFields = [
              formFormulaPointRefill,
              formFormulaOrderSize
          ]
          for (let el of requiredFields) {
              if (!el.checkValidity()) {
                  el.reportValidity()
                  return false
              }
          }
          return true
      }

      function algorithmSaveNew() {
          let xhr = new XMLHttpRequest()
          xhr.onload = () => {
              let resp = JSON.parse(xhr.response)
              console.log(resp)
              algorithmID = resp['id']
              btnSaveAlgorithm.innerText = 'Обновить модель'
          }
          xhr.onerror = err => {
              console.error(err)
          }
          xhr.open('POST', '/api/v1/algorithms/')
          xhr.setRequestHeader('Content-Type', 'application/json')
          xhr.setRequestHeader('X-CSRFToken', form['csrfmiddlewaretoken'].value)
          xhr.send(algorithmPrepareBody())
      }

      function algorithmUpdate() {
          let xhr = new XMLHttpRequest()
          xhr.onload = () => {
              let resp = JSON.parse(xhr.response)
              console.log(resp)
          }
          xhr.onerror = err => {
              console.error(err)
          }
          xhr.open('PUT', `/api/v1/algorithms/${algorithmID}/`)
          xhr.setRequestHeader('Content-Type', 'application/json')
          xhr.setRequestHeader('X-CSRFToken', form['csrfmiddlewaretoken'].value)
          xhr.send(algorithmPrepareBody())
      }

      function algorithmPrepareBody() {
          return JSON.stringify({
              formula_point_refill: formFormulaPointRefill.value,
              formula_order_size: formFormulaOrderSize.value,
              formula_score: formFormulaScore.value,
              is_public: formFormulaIsPublic.checked,
              description: formFormulaDescription.value,
          })
      }
