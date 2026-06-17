# 1. 使用官方轻量级的 Python 3.11 镜像作为基础环境
FROM python:3.11-slim

# 2. 设置容器内部的工作目录
WORKDIR /app

# 3. 将本地的依赖文件复制到容器中
COPY requirements.txt .

# 4. 清华源加速，并安装 Python 依赖（不生成缓存以减小镜像体积）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 5. 将当前目录下的所有项目代码和静态文件复制到容器的工作目录中
COPY . .

# 6. 声明容器运行时监听的端口（FastAPI 默认 8000）
EXPOSE 8000

# 7. 容器启动时默认执行的命令，运行 uvicorn 服务器
CMD ["uvicorn", "calculator:app", "--host", "0.0.0.0", "--port", "0.0.0.0"]

