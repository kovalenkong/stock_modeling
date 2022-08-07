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