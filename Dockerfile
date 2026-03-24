FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-engine.txt && \
    pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 aioredis==2.0.1

# Copy application code
COPY src ./src
COPY tests ./tests

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python3", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
