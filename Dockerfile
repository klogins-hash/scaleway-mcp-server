# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv via pip
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY scaleway_http_server.py .

# Expose port (Scaleway will inject PORT env var)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application
CMD ["uv", "run", "scaleway_http_server.py"]
