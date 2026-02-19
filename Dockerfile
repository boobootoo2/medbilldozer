# MedBillDozer FastAPI Backend - Docker Image for Google Cloud Run

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Copy existing medbilldozer source code (reuse existing modules)
COPY src ./src

# Set Python path to include src directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port (Cloud Run will set PORT env var, default to 8080)
ENV PORT=8080
EXPOSE ${PORT}

# Set production environment
ENV ENVIRONMENT=production
ENV DEBUG=false

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')"

# Run FastAPI with Uvicorn (use PORT from env, multiple workers for production)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2
