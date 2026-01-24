# ContraVento Backend - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Configure poetry to not create virtual env (we're already in container)
RUN poetry config virtualenvs.create false

# Generate lock file and install dependencies (production only, no dev dependencies)
RUN poetry lock --no-update && poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Development (with hot reload)
FROM python:3.12-slim AS development

# Set working directory
WORKDIR /app

# Install runtime dependencies and debugging tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for development
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Configure poetry to not create virtual env
RUN poetry config virtualenvs.create false

# Install all dependencies (including dev dependencies for hot reload)
# Poetry will use poetry.lock if it exists in the build context, otherwise it will generate it
# This ensures the build works whether poetry.lock is committed or not
RUN poetry lock --no-update && poetry install --no-interaction --no-ansi

# Copy application code (will be mounted as volume in docker-compose)
COPY src/ ./src/
COPY alembic.ini ./
COPY scripts/ ./scripts/
COPY config/ ./config/

# Make entrypoint script executable
RUN chmod +x scripts/docker-entrypoint.sh

# Create storage directory
RUN mkdir -p storage/profile_photos storage/trip_photos

# Expose port
EXPOSE 8000

# Use entrypoint script to run migrations and seed data
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

# Development server with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production Runtime
FROM python:3.12-slim AS production

# Set working directory
WORKDIR /app

# Install runtime dependencies and debugging tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY scripts/ ./scripts/
COPY config/ ./config/
# TEMPORAL: Copiar pyproject.toml y poetry.lock para poder usar Poetry en producción
COPY pyproject.toml poetry.lock ./

# Make entrypoint script executable
RUN chmod +x scripts/docker-entrypoint.sh

# Create storage directory
RUN mkdir -p storage/profile_photos storage/trip_photos

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Use entrypoint script to run migrations (no seed data in production)
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

# Production server (no reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
