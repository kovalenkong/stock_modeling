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