# Multi-stage Dockerfile for Flask application
# Stage 1: Builder stage
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install gunicorn for production WSGI server
RUN pip install --no-cache-dir gunicorn==21.2.0

# Copy application code
COPY app.py .
COPY database.py .
COPY schema.sql .
COPY migrations/ ./migrations/
COPY static/ ./static/
COPY templates/ ./templates/
COPY parsers/ ./parsers/
COPY serializers/ ./serializers/
COPY converters/ ./converters/
COPY generators/ ./generators/
COPY utils/ ./utils/

# Create data directory for SQLite database persistence
RUN mkdir -p /app/data

# Set environment variables for production
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Expose port 5000
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/').read()" || exit 1

# Run gunicorn with production settings
# -w 4: 4 worker processes
# -b 0.0.0.0:5000: Bind to all interfaces on port 5000
# --timeout 120: Increase timeout for long-running requests
# --access-logfile -: Log to stdout
# --error-logfile -: Log errors to stdout
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
