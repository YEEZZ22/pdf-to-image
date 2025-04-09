# 使用官方 Python 3.10 映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製當前目錄內容到容器中
COPY . /app

# 安裝 Poppler 和需要的 Python 套件
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    pip install --no-cache-dir -r requirements.txt

# 設定容器啟動命令
CMD ["gunicorn", "-b", "0.0.0.0:5000", "printscreen_app:app"]
