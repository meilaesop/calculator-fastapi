#!/usr/bin/env python3
"""FastAPI 科学计算器：页面服务与安全表达式计算 API。"""

import math
import os
import re
from pathlib import Path
from typing import Literal, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MAX_EXPRESSION_LENGTH = 256
MAX_TOKENS = 100
MAX_NESTING = 32

app = FastAPI(title="Scientific Calculator")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class CalculationRequest(BaseModel):
    expr: str = Field(min_length=1, max_length=MAX_EXPRESSION_LENGTH)
    angle_mode: Literal["DEG", "RAD"] = "DEG"
    ans: float = Field(default=0, ge=-1e100, le=1e100, allow_inf_nan=False)


class ExpressionParser:
    """解析只包含白名单运算符、常数和数学函数的表达式。"""

    _token_pattern = re.compile(
        r"\s*((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[A-Za-z]+|π|\*\*|[()+\-*/%^!])"
    )
    _functions = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "abs": abs,
    }

    def __init__(self, expression: str, angle_mode: Literal["DEG", "RAD"], ans: float) -> None:
        if not expression.strip():
            raise ValueError("表达式不能为空")
        if len(expression) > MAX_EXPRESSION_LENGTH:
            raise ValueError(f"表达式不能超过 {MAX_EXPRESSION_LENGTH} 个字符")

        self.angle_mode = angle_mode
        self.ans = ans
        self.tokens = self._tokenize(expression)
        self.position = 0
        self.nesting = 0

    @classmethod
    def _tokenize(cls, expression: str) -> list[str]:
        tokens = []
        position = 0
        while position < len(expression):
            match = cls._token_pattern.match(expression, position)
            if match is None:
                if expression[position:].strip() == "":
                    break
                raise ValueError("表达式包含不支持的字符")
            tokens.append(match.group(1))
            if len(tokens) > MAX_TOKENS:
                raise ValueError("表达式过于复杂")
            position = match.end()
        return tokens

    def _peek(self) -> str | None:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def _take(self) -> str:
        token = self._peek()
        if token is None:
            raise ValueError("表达式不完整")
        self.position += 1
        return token

    def _parse_expression(self) -> float:
        value = self._parse_term()
        while self._peek() in ("+", "-"):
            operator = self._take()
            right = self._parse_term()
            value = value + right if operator == "+" else value - right
        return value

    def _starts_primary(self, token: str | None) -> bool:
        return token is not None and (token[0].isdigit() or token[0].isalpha() or token[0] in "π(")

    def _parse_term(self) -> float:
        value = self._parse_unary()
        while self._peek() in ("*", "/", "%") or self._starts_primary(self._peek()):
            token = self._peek()
            operator = self._take() if token in ("*", "/", "%") else "*"
            right = self._parse_unary()
            if operator == "/":
                if right == 0:
                    raise ValueError("除数不能为零")
                value /= right
            elif operator == "%":
                if right == 0:
                    raise ValueError("取模数不能为零")
                value %= right
            else:
                value *= right
            self._check_finite(value)
        return value

    def _parse_unary(self) -> float:
        if self._peek() == "+":
            self._take()
            return self._parse_unary()
        if self._peek() == "-":
            self._take()
            return -self._parse_unary()
        return self._parse_power()

    def _parse_power(self) -> float:
        base = self._parse_postfix()
        if self._peek() in ("^", "**"):
            self._take()
            exponent = self._parse_unary()
            if abs(exponent) > 100:
                raise ValueError("指数绝对值不能超过 100")
            if base == 0 and exponent < 0:
                raise ValueError("零不能进行负数次幂运算")
            if base < 0 and not exponent.is_integer():
                raise ValueError("负数不能进行非整数次幂运算")
            try:
                base = base ** exponent
            except OverflowError as error:
                raise ValueError("幂运算结果超出允许范围") from error
        self._check_finite(base)
        return base

    def _parse_postfix(self) -> float:
        value = self._parse_primary()
        while self._peek() == "!":
            self._take()
            if not value.is_integer() or value < 0:
                raise ValueError("阶乘仅支持非负整数")
            if value > 69:
                raise ValueError("阶乘结果超出允许范围（最大支持 69!）")
            value = float(math.factorial(int(value)))
        return value

    def _parse_primary(self) -> float:
        token = self._take()
        if token == ")":
            raise ValueError("右括号位置错误")
        if token in ("!", "^", "**", "%", "*", "/"):
            raise ValueError("运算符位置错误")
        if token == "(":
            self.nesting += 1
            if self.nesting > MAX_NESTING:
                raise ValueError("表达式嵌套过深")
            try:
                value = self._parse_expression()
                if self._take() != ")":
                    raise ValueError("括号不匹配")
                return value
            finally:
                self.nesting -= 1

        if token[0].isdigit() or token[0] == ".":
            return self._check_finite(float(token))

        name = token.lower()
        if name in ("π", "pi"):
            return math.pi
        if name == "e":
            return math.e
        if name == "ans":
            return self.ans

        function = self._functions.get(name)
        if function is None:
            raise ValueError(f"不支持的函数或常数：{token}")
        self.nesting += 1
        if self.nesting > MAX_NESTING:
            raise ValueError("表达式嵌套过深")
        try:
            if self._take() != "(":
                raise ValueError(f"{name} 函数需要括号")
            argument = self._parse_expression()
            if self._take() != ")":
                raise ValueError("括号不匹配")
        finally:
            self.nesting -= 1

        if name in ("sin", "cos", "tan") and self.angle_mode == "DEG":
            argument = math.radians(argument)
        if name == "sqrt" and argument < 0:
            raise ValueError("平方根的被开方数不能小于零")
        if name in ("log", "ln") and argument <= 0:
            raise ValueError("对数的真数必须大于零")
        if name in ("asin", "acos") and not -1 <= argument <= 1:
            raise ValueError("反三角函数的输入必须在 -1 到 1 之间")
        try:
            result = function(argument)
        except OverflowError as error:
            raise ValueError("函数计算结果超出允许范围") from error
        if name in ("asin", "acos", "atan") and self.angle_mode == "DEG":
            result = math.degrees(result)
        return self._check_finite(result)

    @staticmethod
    def _check_finite(value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("结果无效，请检查输入范围")
        if abs(value) > 1e100:
            raise ValueError("计算结果超出允许范围")
        return value

    def parse(self) -> float:
        result = self._parse_expression()
        if self.position != len(self.tokens):
            raise ValueError("表达式格式错误")
        return self._check_finite(result)


@app.get("/")
async def index() -> FileResponse:
    """返回科学计算器页面。"""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/calculate")
async def calculate(request: CalculationRequest) -> dict[str, Union[float, str]]:
    """计算经过限制的数学表达式，并返回结果及格式化值。"""
    try:
        parser = ExpressionParser(request.expr, request.angle_mode, request.ans)
        result = parser.parse()
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, RecursionError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "result": result,
        "formatted": f"{result:.12g}",
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() in {"1", "true", "yes"}

    uvicorn.run("calculator:app", host=host, port=port, reload=reload)
