# 科学计算器

一款面向日常计算和数学学习的全栈科学计算器。项目采用 FastAPI 提供页面服务与计算 API，原生 JavaScript 负责输入交互和结果展示。

## 项目亮点

- **科学计算**：支持三角函数及反三角函数、平方根、平方、幂、阶乘、倒数、百分比、对数、自然对数和绝对值。
- **常数与连续计算**：支持 π、e 和 Ans（上一次计算结果）。
- **角度切换**：支持 DEG（角度）和 RAD（弧度）模式。
- **后端表达式解析**：FastAPI 使用受限的词法与递归下降解析器计算表达式，不通过 `eval` 或 `new Function` 执行输入。
- **输入校验**：限制表达式长度、令牌数量、括号嵌套、幂指数与结果范围；错误以明确的 HTTP 状态码返回。
- **前后端分离**：浏览器通过 JSON API 提交表达式与角度模式，后端完成计算并返回格式化结果。
- **响应式界面**：适配桌面和窄屏设备，提供清晰的表达式与结果显示。

## 技术栈

- Python 3
- FastAPI、Pydantic
- Uvicorn
- HTML、CSS、原生 JavaScript

## 本地运行

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python calculator.py
```

打开浏览器访问 <http://127.0.0.1:8000>。

开发时也可以使用自动重载：

```powershell
uvicorn calculator:app --reload
```

如果 `python` 命令不可用，请使用电脑上已安装的 Python 完整路径替换命令中的 `python`。

## 测试

安装项目依赖后运行测试：

```powershell
python -m pip install -r requirements.txt
python -m unittest tests.test_calculator -v
```

## API

### `POST /api/calculate`

请求：

```json
{
  "expr": "sin(30) + sqrt(16)",
  "angle_mode": "DEG",
  "ans": 0
}
```

成功响应：

```json
{
  "result": 4.5,
  "formatted": "4.5"
}
```

`angle_mode` 支持 `DEG` 和 `RAD`；`ans` 是可选的上次计算结果。表达式错误会返回 HTTP 400，字段校验错误会返回 HTTP 422。

## 键盘操作

| 按键 | 功能 |
| --- | --- |
| `0`–`9`、`.` | 输入数字 |
| `+`、`-`、`*`、`/`、`%`、`^`、`**`、括号 | 输入运算符 |
| 函数字母 | 仅允许输入支持的函数与常数名称，如 `sin`、`sqrt`、`pi`、`e`、`ans`；无效名称会被拦截 |
| 其他字符 | 仅接受支持的运算符和括号；不支持的字符会被拦截并提示 |
| `Enter` 或 `=` | 计算 |
| `Backspace` | 删除最后一个字符 |
| `Escape` | 清空表达式 |
| `pi`、`e`、`ans` | 输入圆周率、自然常数或上次结果 |

阶乘受结果范围限制，当前最大支持 `69!`；负数的非整数次幂、无效函数输入和超范围计算会显示中文错误提示。

## Docker 运行

```powershell
docker build -t scientific-calculator .
docker run --rm -p 8000:8000 scientific-calculator
```

然后访问 <http://127.0.0.1:8000>。

## 项目结构

```text
calculator-fastapi/
├── .dockerignore           # Docker 构建忽略规则
├── .gitignore              # Git 忽略规则
├── Dockerfile              # Docker 镜像构建配置
├── calculator.py           # FastAPI 页面服务和科学计算 API
├── requirements.txt        # 运行及测试依赖
├── README.md               # 项目介绍与运行说明
├── static/
│   ├── index.html          # 科学计算器页面
│   ├── style.css           # 响应式界面样式
│   └── app.js              # 按键交互和 API 调用
└── tests/
    └── test_calculator.py  # API 与表达式解析测试
```

## 作品集展示信息

**项目简介：** 基于 FastAPI 和原生 JavaScript 开发的全栈网页科学计算器。后端提供安全的数学表达式解析 API，前端支持科学函数、角度/弧度切换与连续计算。

**推荐技术标签：** Python、FastAPI、Pydantic、JavaScript、HTML、CSS、REST API、表达式解析。

**上传前建议：** 启动项目并截取一张实际运行页面；如果部署了在线演示，可填写真实可访问的演示地址。
