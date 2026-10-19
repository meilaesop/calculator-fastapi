import unittest

from fastapi.testclient import TestClient

from calculator import app


class CalculatorApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_scientific_operations(self):
        cases = (
            ("sin(30)", "DEG", 0.5),
            ("asin(0.5)", "DEG", 30),
            ("sqrt(9) + 2^3", "DEG", 11),
            ("6**2", "DEG", 36),
            ("2**3", "DEG", 8),
            ("2**3**2", "DEG", 512),
            ("2*3**2", "DEG", 18),
            ("5!", "DEG", 120),
            ("2π", "RAD", 6.283185307179586),
            ("1e3", "RAD", 1000),
            ("ans + 2", "RAD", 7, 5),
        )

        for case in cases:
            expression, angle_mode, expected, *answer = case
            response = self.client.post(
                "/api/calculate",
                json={
                    "expr": expression,
                    "angle_mode": angle_mode,
                    "ans": answer[0] if answer else 0,
                },
            )
            with self.subTest(expression=expression):
                self.assertEqual(response.status_code, 200)
                self.assertAlmostEqual(response.json()["result"], expected)

    def test_invalid_expressions_are_rejected(self):
        expected_errors = {
            "1 / 0": "除数不能为零",
            "sqrt(-1)": "平方根的被开方数不能小于零",
            "2@3": "表达式包含不支持的字符",
            "foo(2)": "不支持的函数或常数：foo",
            "2^101": "指数绝对值不能超过 100",
            "(9)+)": "右括号位置错误",
            "ln(0)": "对数的真数必须大于零",
            "asin(2)": "反三角函数的输入必须在 -1 到 1 之间",
            "(-1)^0.5": "负数不能进行非整数次幂运算",
            "100!": "阶乘结果超出允许范围（最大支持 69!）",
            "exp(1000)": "函数计算结果超出允许范围",
            "!": "运算符位置错误",
        }
        for expression, expected_error in expected_errors.items():
            response = self.client.post("/api/calculate", json={"expr": expression})
            with self.subTest(expression=expression):
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["detail"], expected_error)

    def test_request_validation_and_unknown_route(self):
        self.assertEqual(
            self.client.post("/api/calculate", json={"expr": "1", "angle_mode": "GRAD"}).status_code,
            422,
        )
        self.assertEqual(
            self.client.post("/api/calculate", json={"expr": "1" * 257}).status_code,
            422,
        )
        self.assertEqual(self.client.post("/api/calc", json={"expr": "1+1"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
