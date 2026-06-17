# FastAPI 计算器应用

一个基于 FastAPI 框架构建的现代化计算器应用，提供优美的 UI 界面和完整的中文代码注释。

## 🚀 功能特点

- **现代化 UI** - 深色主题设计，响应式布局
- **完整注释** - 所有代码都配有详细的中文注释，便于学习
- **RESTful API** - `/api/calc` 端点支持 POST 和 GET 请求
- **安全计算** - 使用 AST 模块安全解析表达式，防止代码注入
- **键盘支持** - 支持鼠标点击和键盘输入

## 📋 支持的操作

- ➕ 加法 `+`
- ➖ 减法 `-`
- ✖️ 乘法 `*`
- ➗ 除法 `/`
- 📊 取模 `%`
- ⬆️ 乘方 `**`

## 🛠 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 运行应用

```powershell
python calculator.py
```

或使用 uvicorn 直接运行：

```powershell
uvicorn calculator:app --reload
```

### 3. 打开浏览器

访问 `http://127.0.0.1:8000` 使用计算器

## 📁 项目结构

```
calculator-fastapi/
├── calculator.py          # FastAPI 后端应用
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── .gitignore            # Git 忽略配置
└── static/               # 静态文件目录
    ├── index.html        # 计算器 UI
    ├── style.css         # 样式表
    └── app.js            # 前端交互逻辑
```

## 🔌 API 端点

### POST /api/calc

计算数学表达式

**请求示例：**
```json
{
  "expr": "2+3*4"
}
```

**响应示例：**
```json
{
  "result": 14
}
```

### GET /api/calc

通过 URL 参数计算表达式

**请求示例：**
```
GET /api/calc?expr=10+5*2
```

**响应示例：**
```json
{
  "result": 20
}
```

## ⌨️ 键盘快捷键

| 按键 | 功能 |
|-----|------|
| `0-9` | 输入数字 |
| `+` `-` `*` `/` | 输入操作符 |
| `Enter` | 计算结果 |
| `Backspace` | 删除最后一个字符 |
| `Escape` | 清空表达式 |

## 📝 代码说明

所有代码都包含详细的中文注释：

- **calculator.py** - 后端应用逻辑和 API 端点
- **static/index.html** - HTML 页面结构
- **static/style.css** - CSS 样式（深色主题）
- **static/app.js** - 前端交互和 API 调用

## 🔒 安全性

使用 Python 的 AST（抽象语法树）模块安全地解析和计算表达式：

- 只允许特定的数学操作符
- 防止任意代码执行
- 完整的输入验证

## 📦 依赖

- FastAPI - 现代 Python Web 框架
- Uvicorn - ASGI Web 服务器
- Pydantic - 数据验证库

## 🎓 学习资源

这个项目非常适合学习：

- FastAPI 框架的基础使用
- 如何构建 RESTful API
- 前后端交互的最佳实践
- Python 的 AST 模块用法
- 现代化 Web UI 设计

## 📄 许可证

MIT
