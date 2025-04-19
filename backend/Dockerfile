FROM python:3.10-slim  

WORKDIR /app  

# 设置环境变量  
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1  

# 安装依赖  
COPY requirements.txt .  
RUN pip install --no-cache-dir --upgrade -r requirements.txt  

# 复制代码  
COPY . .  

# 创建非root用户  
RUN adduser --disabled-password --gecos "" appuser  
USER appuser  

# 运行应用  
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]  