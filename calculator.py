#!/usr/bin/env python3
"""
FastAPI 计算器应用

功能：
1. 提供现代化计算器 UI
2. 安全地评估数学表达式
3. 通过 RESTful API 返回计算结果

作者: Calculator App
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import ast
import operator as op

# =============== 应用初始化 ===============
# 创建 FastAPI 应用实例
app = FastAPI(title="Calculator App")

# 挂载静态文件目录，允许直接访问 HTML/CSS/JS
# URL 路径 /static 映射到本地 static/ 文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============== 路由定义 ===============
@app.get("/")
async def index():
	"""
	主页路由 - 返回计算器 HTML
	当用户访问 http://127.0.0.1:8000/ 时调用
	"""
	return FileResponse("static/index.html")


# =============== 数据模型 ===============
class CalcRequest(BaseModel):
	"""POST /api/calc 请求的数据模型"""
	expr: str  # 数学表达式字符串，如 "3+5*2"


# =============== 允许的操作符 ===============
# 定义允许使用的操作符映射
# 将 AST 节点类型映射到对应的 Python 操作函数
# 这样做是为了安全考虑，只允许基本数学操作
_ALLOWED_OPS = {
	ast.Add: op.add,      # 加法 (+)
	ast.Sub: op.sub,      # 减法 (-)
	ast.Mult: op.mul,     # 乘法 (*)
	ast.Div: op.truediv,  # 除法 (/)
	ast.Pow: op.pow,      # 幂运算 (**)
	ast.Mod: op.mod,      # 取模 (%)
	ast.USub: op.neg,     # 一元负号 (-)
}


# =============== 表达式计算函数 ===============
def _eval_expr(expr: str):
	"""
	安全地评估数学表达式

	原理：
	1. 使用 Python 的 AST（抽象语法树）模块解析表达式
	2. 递归遍历 AST，只允许特定的操作（加减乘除等）
	3. 不允许任意代码执行，防止注入攻击

	参数:
		expr (str): 数学表达式字符串
					示例: "2+3*4", "10/2-1", "(5+3)*2"

	返回:
		int | float: 计算结果

	异常:
		ValueError: 
			- 表达式包含不允许的操作
			- 表达式语法错误
			- 包含不支持的表达式类型
	"""
	# 将字符串解析成 AST（抽象语法树）
	# mode="eval" 表示解析为表达式（而不是语句）
	node = ast.parse(expr, mode="eval")

	def _eval(n):
		"""
		递归函数：评估 AST 节点

		参数:
			n: AST 节点

		返回:
			该节点代表的值
		"""

		# 情况 1: 常数节点（数字字面量）
		# 例如: 3, 3.14, 100
		if isinstance(n, ast.Constant):
			# 只允许整数和浮点数
			if isinstance(n.value, (int, float)):
				return n.value
			raise ValueError("不支持的常数类型")

		# 情况 2: 二元操作节点
		# 例如: 3+5, 10*2, 6-4 等
		if isinstance(n, ast.BinOp):
			# 递归计算左操作数
			left = _eval(n.left)
			# 递归计算右操作数
			right = _eval(n.right)
			# 根据操作符类型获取对应的函数
			op_func = _ALLOWED_OPS.get(type(n.op))
			# 检查操作符是否被允许
			if op_func is None:
				raise ValueError("不支持的操作符")
			# 执行操作并返回结果
			return op_func(left, right)

		# 情况 3: 一元操作节点
		# 例如: -5（负数）
		if isinstance(n, ast.UnaryOp):
			# 获取一元操作符对应的函数
			op_func = _ALLOWED_OPS.get(type(n.op))
			if op_func is None:
				raise ValueError("不支持的一元操作符")
			# 对操作数应用操作符
			return op_func(_eval(n.operand))

		# 如果是其他类型的节点，抛出错误
		raise ValueError("不支持的表达式类型")

	# 从 AST 的根节点开始计算整个表达式
	return _eval(node.body)


# =============== API 端点 ===============
@app.post("/api/calc")
async def calc_post(req: CalcRequest):
	"""
	POST 端点 - 计算表达式

	接收 JSON 格式的请求:
		{
			"expr": "2+3*4"
		}

	返回 JSON 格式的结果:
		{
			"result": 14
		}

	HTTP 状态码:
		200: 计算成功
		400: 表达式无效或计算错误
	"""
	try:
		# 验证表达式不为空
		if not req.expr or not req.expr.strip():
			raise ValueError("表达式不能为空")

		# 计算表达式（去掉首尾空格）
		result = _eval_expr(req.expr.strip())
		# 返回计算结果
		return {"result": result}

	except Exception as e:
		# 打印错误日志便于调试
		print(f"计算错误 '{req.expr}': {e}")
		# 返回 400 Bad Request 和错误信息
		raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/calc")
async def calc_get(expr: str):
	"""
	GET 端点 - 计算表达式

	接收 URL 参数格式的请求:
		/api/calc?expr=2+3*4

	返回 JSON 格式的结果:
		{
			"result": 14
		}

	HTTP 状态码:
		200: 计算成功
		400: 表达式无效或计算错误
	"""
	try:
		# 计算表达式
		result = _eval_expr(expr)
		return {"result": result}
	except Exception as e:
		# 返回错误信息
		raise HTTPException(status_code=400, detail=str(e))


# =============== 应用入口 ===============
if __name__ == "__main__":
	import uvicorn

	# 启动 Uvicorn Web 服务器
	uvicorn.run(
		"calculator:app",            # 模块名:应用变量名
		host="127.0.0.1",            # 监听地址（仅本地）
		port=8000,                   # 监听端口
		reload=True                  # 开发模式：代码修改后自动重启
	)
