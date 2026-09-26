FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app/ ./app/

# Download model from GitHub Release
RUN mkdir -p app/models/saved && \
    curl -L -o app/models/saved/agrivision_v1.pth \
    https://github.com/brianshitambasi/agrivision-ai/releases/download/v1.0-model/agrivision_v1.pth

# Environment
ENV MODEL_PATH=app/models/saved/agrivision_v1.pth
ENV DEVICE=cpu
ENV PORT=8000
ENV CONFIDENCE_THRESHOLD=0.75

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
