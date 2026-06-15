# 锁定 Python 3.11：onnxruntime / rapidocr 在 3.11 有现成 wheel，
# 规避本地 Python 3.14 无预编译包的问题。
FROM python:3.11-slim

# RapidOCR 依赖 opencv(cv2)，需要这些系统库；libxcb1 等缺失会在 import 时报
# "libxcb.so.1: cannot open shared object file"。PyMuPDF/pillow 也用得到。
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libxcb1 \
    libxrender1 \
    libsm6 \
    libxext6 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖以利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预热 RapidOCR 模型权重，避免首个请求时才下载（构建期固化进镜像）
RUN python -c "from rapidocr_onnxruntime import RapidOCR; RapidOCR()" || true

COPY src ./src

ENV HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Streamable HTTP MCP 端点默认挂在 /mcp
CMD ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
