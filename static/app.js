/**
 * FastAPI 计算器 - 前端 JavaScript
 * 
 * 功能：
 * 1. 管理计算器显示屏
 * 2. 处理用户按钮点击事件
 * 3. 支持键盘输入
 * 4. 通过 API 调用后端计算表达式
 */

// ===== IIFE 模式 - 立即执行函数表达式 =====
// 目的：创建独立的作用域，避免全局变量污染
(() => {
    // ===== 获取 DOM 元素 =====
    // 获取显示屏元素，用于显示表达式和计算结果
    const display = document.getElementById('display')

    // ===== 状态变量 =====
    // 当前表达式字符串，例如 "3+5" 或 "10*2"
    let expr = ''

    // ===== 渲染函数 =====
    /**
     * 更新显示屏内容
     * 
     * 功能：将当前表达式更新到 HTML 中
     * 如果表达式为空，显示 '0'
     */
    function render() {
        display.textContent = expr || '0'
    }

    // ===== 计算函数 =====
    /**
     * 发送表达式到后端进行计算
     * 
     * 参数:
     *   expression (string): 要计算的数学表达式
     * 
     * 过程：
     *   1. 验证表达式不为空或不完整
     *   2. 发送 POST 请求到 /api/calc
     *   3. 接收 JSON 响应，提取结果
     *   4. 更新显示屏
     *   5. 捕获错误并显示错误信息
     */
    async function compute(expression) {
        try {
            // ===== 表达式验证 =====

            // 检查表达式是否为空
            if (!expression || !expression.trim()) {
                expr = 'Error: 空表达式'
                render()
                return
            }

            // 检查表达式是否以操作符结尾（不完整）
            // 正则表达式 /[+\-*/]$/ 匹配以 +、-、*、/ 结尾的字符串
            if (/[+\-*/]$/.test(expression.trim())) {
                expr = 'Error: 不完整'
                render()
                return
            }

            // ===== 发送 API 请求 =====
            const res = await fetch('/api/calc', {
                method: 'POST',              // HTTP 方法
                headers: {
                    'Content-Type': 'application/json'  // 请求头：JSON 格式
                },
                body: JSON.stringify({
                    expr: expression.trim()  // 请求体：要计算的表达式
                })
            })

            // ===== 解析响应 =====
            const data = await res.json()    // 解析 JSON 响应

            // 检查响应状态是否成功
            if (!res.ok) throw data          // 如果失败，抛出错误

            // ===== 更新表达式和显示屏 =====
            expr = String(data.result)      // 将结果转换为字符串并保存
            render()                         // 更新显示屏

        } catch (err) {
            // ===== 错误处理 =====
            console.error('计算错误:', err)  // 在控制台打印错误（便于调试）
            expr = 'Error'                  // 显示错误提示
            render()
        }
    }

    // ===== 按钮点击事件监听 =====
    /**
     * 为所有按钮添加点击事件监听
     * 根据按钮的 data-action 属性执行不同的操作
     */
    document.querySelectorAll('.keys button').forEach(btn => {
        btn.addEventListener('click', e => {
            // 获取按钮的 data-action 属性（如果有）
            const action = btn.dataset.action

            // 获取按钮的文本内容（数字或符号）
            const val = btn.textContent

            // ===== 根据不同操作执行逻辑 =====
            if (action === 'clear') {
                // 清空：清除表达式
                expr = ''

            } else if (action === 'back') {
                // 删除：移除最后一个字符
                expr = expr.slice(0, -1)

            } else if (action === 'equals') {
                // 等号：计算表达式
                if (expr) compute(expr)

            } else if (action === 'op') {
                // 操作符：追加操作符到表达式
                expr += val

            } else {
                // 数字和小数点：追加到表达式
                expr += val
            }

            // 更新显示屏
            render()
        })
    })

    // ===== 键盘支持 =====
    /**
     * 添加键盘事件监听，支持键盘输入
     * 用户可以直接用键盘输入数字和操作符
     */
    window.addEventListener('keydown', e => {
        // ===== 数字和操作符键 =====
        // 正则表达式 /^[0-9+\-*/().]$/ 匹配数字、操作符和小数点
        if ((/^[0-9+\-*/().]$/).test(e.key)) {
            expr += e.key       // 追加到表达式
            render()

            // ===== 回车键 - 计算结果 =====
        } else if (e.key === 'Enter') {
            if (expr) compute(expr)

            // ===== 退格键 - 删除最后一个字符 =====
        } else if (e.key === 'Backspace') {
            expr = expr.slice(0, -1)
            render()

            // ===== ESC 键 - 清空表达式 =====
        } else if (e.key === 'Escape') {
            expr = ''
            render()
        }
    })

    // ===== 初始化 =====
    // 页面加载时，初始化显示屏
    render()
})()

/* 
   ===== 使用说明 =====
   
   1. 鼠标输入：点击按钮输入数字和操作符，按"="计算
   
   2. 键盘输入：
      - 数字/操作符：直接按键盘输入
      - 计算：按 Enter
      - 删除：按 Backspace
      - 清空：按 Escape
   
   3. 特殊按钮：
      - C：清空所有输入
      - ←：删除最后一个字符
      - =：计算表达式
   
   4. 支持的操作：
      - 加法 (+)
      - 减法 (-)
      - 乘法 (*)
      - 除法 (/)
      - 取模 (%)
      - 乘方 (**)
   
   5. 错误处理：
      - 空表达式：显示 "Error: 空表达式"
      - 不完整表达式：显示 "Error: 不完整"
      - 其他错误：显示 "Error"
*/
