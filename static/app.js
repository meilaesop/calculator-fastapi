(() => {
    const expressionDisplay = document.getElementById('expression')
    const display = document.getElementById('display')
    const modeToggle = document.getElementById('mode-toggle')
    const keyHelp = document.getElementById('key-help')
    const keyHelpText = document.getElementById('key-help-text')

    let expression = ''
    let lastResult = 0
    let angleMode = 'DEG'
    let justEvaluated = false
    let calculationId = 0
    const supportedNames = [
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'sqrt', 'log', 'ln', 'exp', 'abs', 'pi', 'e', 'ans',
    ]

    function render(result = null) {
        const displayValue = result === null ? (expression ? '' : '0') : String(result)
        expressionDisplay.textContent = expression
        display.textContent = displayValue
        expressionDisplay.setAttribute('aria-label', expression)
        display.setAttribute('aria-label', displayValue)
        modeToggle.textContent = angleMode
        modeToggle.setAttribute('aria-label', `角度模式：${angleMode}，点击切换`)
    }

    function showInputError(message) {
        display.textContent = message
        display.setAttribute('aria-label', message)
    }

    function showKeyHelp(button) {
        keyHelpText.textContent = button.dataset.help
        keyHelp.classList.add('is-visible')
        keyHelp.setAttribute('aria-hidden', 'false')
        button.setAttribute('aria-describedby', 'key-help')
    }

    function hideKeyHelp(button) {
        keyHelp.classList.remove('is-visible')
        keyHelp.setAttribute('aria-hidden', 'true')
        button.removeAttribute('aria-describedby')
    }

    function append(value, startNew = false) {
        calculationId += 1
        if (justEvaluated) {
            expression = startNew ? '' : String(lastResult)
            justEvaluated = false
        }
        expression += value
        render()
    }

    function canAppendLetter(letter) {
        const currentExpression = justEvaluated ? '' : expression
        const candidate = `${currentExpression}${letter}`
        const name = candidate.match(/[a-z]+$/i)?.[0].toLowerCase()
        return name !== undefined && supportedNames.some(supportedName => supportedName.startsWith(name))
    }

    function toggleAngleMode() {
        calculationId += 1
        angleMode = angleMode === 'DEG' ? 'RAD' : 'DEG'
        render()
    }

    async function calculate() {
        if (!expression.trim()) {
            render(0)
            return
        }

        const requestId = ++calculationId
        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    expr: expression,
                    angle_mode: angleMode,
                    ans: lastResult,
                }),
            })
            const data = await response.json()
            if (!response.ok) throw new Error(data.detail || '计算失败')
            if (requestId !== calculationId) return

            lastResult = data.result
            justEvaluated = true
            render(data.formatted)
        } catch (error) {
            if (requestId !== calculationId) return
            const errorMessages = {
                'float division by zero': '除数不能为零',
                'math domain error': '函数输入超出定义范围',
                'math range error': '函数计算结果超出允许范围',
                'must be real number, not complex': '负数不能进行非整数次幂运算',
                'int too large to convert to float': '计算结果超出允许范围',
            }
            let message = errorMessages[error.message] || error.message
            if (error.message === '计算结果超出允许范围' && /!\s*$/.test(expression)) {
                message = '阶乘结果超出允许范围（最大支持 69!）'
            } else if (/^不支持的函数或常数：[!^%*/]+$/.test(message)) {
                message = '运算符位置错误'
            }
            display.textContent = message
            display.setAttribute('aria-label', message)
        }
    }

    document.querySelectorAll('.keys button').forEach(button => {
        if (button.dataset.help) {
            button.addEventListener('mouseenter', () => showKeyHelp(button))
            button.addEventListener('mouseleave', () => hideKeyHelp(button))
            button.addEventListener('focus', () => showKeyHelp(button))
            button.addEventListener('blur', () => hideKeyHelp(button))
        }

        button.addEventListener('click', () => {
            const action = button.dataset.action
            const value = button.dataset.value

            if (action === 'clear') {
                calculationId += 1
                expression = ''
                justEvaluated = false
                render()
            } else if (action === 'delete') {
                calculationId += 1
                expression = expression.slice(0, -1)
                justEvaluated = false
                render()
            } else if (action === 'toggle-mode') {
                toggleAngleMode()
            } else if (action === 'equals') {
                calculate()
            } else if (action === 'negate') {
                calculationId += 1
                expression = justEvaluated ? `-(${lastResult})` : expression ? `-(${expression})` : '-'
                justEvaluated = false
                render()
            } else if (action === 'reciprocal') {
                calculationId += 1
                expression = justEvaluated ? `1/(${lastResult})` : expression ? `1/(${expression})` : '1/('
                justEvaluated = false
                render()
            } else if (action === 'percent') {
                calculationId += 1
                expression = justEvaluated ? `(${lastResult})/100` : expression ? `(${expression})/100` : ''
                justEvaluated = false
                render()
            } else if (action === 'square') {
                calculationId += 1
                expression = justEvaluated ? `(${lastResult})^2` : expression ? `(${expression})^2` : ''
                justEvaluated = false
                render()
            } else if (action === 'factorial') {
                calculationId += 1
                if (justEvaluated) expression = String(lastResult)
                justEvaluated = false
                append('!')
            } else if (value) {
                if (justEvaluated && action === 'func' && /^[a-z]+\($/i.test(value)) {
                    calculationId += 1
                    expression = `${value}${lastResult})`
                    justEvaluated = false
                    render()
                } else {
                    append(value, action === 'digit' || (action === 'func' && value !== ')'))
                }
            }
        })
    })

    modeToggle.addEventListener('mouseenter', () => showKeyHelp(modeToggle))
    modeToggle.addEventListener('mouseleave', () => hideKeyHelp(modeToggle))
    modeToggle.addEventListener('focus', () => showKeyHelp(modeToggle))
    modeToggle.addEventListener('blur', () => hideKeyHelp(modeToggle))
    modeToggle.addEventListener('click', toggleAngleMode)

    document.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === '=') {
            event.preventDefault()
            if (document.activeElement instanceof HTMLElement) {
                document.activeElement.blur()
            }
            calculate()
        } else if (event.key === 'Backspace') {
            calculationId += 1
            expression = expression.slice(0, -1)
            justEvaluated = false
            render()
        } else if (event.key === 'Escape') {
            calculationId += 1
            expression = ''
            justEvaluated = false
            render()
        } else if (
            !event.ctrlKey &&
            !event.metaKey &&
            !event.altKey &&
            event.key.length === 1
        ) {
            const isLetter = /^[a-z]$/i.test(event.key)
            if (
                /^[0-9π.()+\-*/%^!]$/u.test(event.key) ||
                (isLetter && canAppendLetter(event.key))
            ) {
                append(event.key, /^[0-9.a-zA-Zπ]$/u.test(event.key))
            } else {
                event.preventDefault()
                showInputError(
                    isLetter
                        ? `不支持的函数或常数名称：${event.key}`
                        : `不支持输入字符：${event.key}`,
                )
            }
        }
    }, true)

    render()
})()
